"""CLI entry point — publish command.

Layer 4 router (v0.3.0): typer commands parse args, build a Pipeline, hand off.
All step logic lives in publish.actions (Layer 2); step orchestration lives
in publish.pipeline (Layer 3); per-command bodies live in publish.commands
(Layer 4 helpers). This file owns only:

  * typer app + sub-typer registration
  * argument-validation for ``deploy``
  * persisted-config loading for ``deploy``
  * wiring actions into a Pipeline for ``deploy``
  * final summary printing for ``deploy``

Non-deploy commands are thin shims that import their body from
``publish.commands.{config,cert,list}``.
"""
import sys
from pathlib import Path
from typing import Optional

import typer

# Force UTF-8 stdout/stderr on Windows so emojis don't crash against cp1252.
if sys.platform == "win32":
    for _sn in ("stdout", "stderr"):
        _s = getattr(sys, _sn, None)
        if _s is None or not hasattr(_s, "buffer") or _s.buffer.closed:
            continue
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from publish.actions import (
    action_dns_create_record,
    action_nginx_deploy,
    action_ssl_request_cert,
)
from publish.cli_helpers import get_dns_provider
from publish.commands.cert import cert_renew, cert_status
from publish.commands.config import config_dns, config_init, config_ssh
from publish.commands.list import list_published_cmd
from publish.config.store import load_dns_config, load_ssh_config
from publish.cockpit.logger import log_publish
from publish.models import PublishOperation, PublishStatus
from publish.pipeline import Pipeline, Step, format_step
from publish.utils.validators import (
    validate_ipv4,
    validate_publish_name,
    validate_subdomain,
    validate_upstream,
    validate_webroot,
)

app = typer.Typer(
    name="publish",
    help="自动网页发布平台 — 一键部署子域名到 Nginx + SSL",
    no_args_is_help=True,
)
config_app = typer.Typer(help="配置管理")
app.add_typer(config_app, name="config")
cert_app = typer.Typer(help="SSL 证书管理")
app.add_typer(cert_app, name="cert")


# ── config ───────────────────────────────────────────────────────────────

@config_app.command("init")
def _config_init():
    """从当前目录的 .env 文件自动生成 DNS + SSH 配置（无需交互）."""
    config_init()


@config_app.command("dns")
def _config_dns(
    provider: str = typer.Option(
        ..., "--provider", "-p", help="DNS 提供商: cloudflare, aliyun, dnspod"
    ),
):
    """配置 DNS 提供商凭据."""
    config_dns(provider=provider)


@config_app.command("ssh")
def _config_ssh(
    host: str = typer.Option(..., "--host", help="云机器 IP 或域名"),
    user: str = typer.Option(..., "--user", help="SSH 用户名"),
    key: Optional[Path] = typer.Option(None, "--key", "-k", help="SSH 私钥路径"),
    port: int = typer.Option(22, "--port", help="SSH 端口"),
):
    """配置 SSH 连接信息."""
    config_ssh(host=host, user=user, port=port, key=key)


# ── deploy (router body — uses Layer 2 + Layer 3) ────────────────────────

@app.command("deploy")
def deploy(
    name: str = typer.Argument(..., help="发布名称（如 app、blog）"),
    domain: str = typer.Option(..., "--domain", "-d", help="完整子域名"),
    webroot: Optional[Path] = typer.Option(
        None, "--webroot", "-w", help="本地网页文件目录（静态模式必填）"
    ),
    proxy: bool = typer.Option(
        False, "--proxy", help="反向代理模式（配合 --upstream，绕过 webroot 校验）"
    ),
    upstream: Optional[str] = typer.Option(
        None, "--upstream", "-r", help="上游 URL，如 http://127.0.0.1:8088"
    ),
    ip: Optional[str] = typer.Option(None, "--ip", help="云机器 IP（DNS A 记录指向）"),
    ssl: bool = typer.Option(True, "--ssl/--no-ssl", help="是否申请 SSL 证书"),
    force: bool = typer.Option(False, "--force", "-f", help="覆盖已有 DNS 记录"),
):
    """完整发布网页到子域名（DNS + Nginx + SSL via Pipeline, v0.3.0)."""
    name = validate_publish_name(name)
    domain = validate_subdomain(domain)
    if ip:
        ip = validate_ipv4(ip)

    if webroot is not None and proxy:
        raise typer.BadParameter("--webroot 与 --proxy 互斥，请选择其一")
    if proxy:
        if not upstream:
            raise typer.BadParameter("--proxy 模式必须配合 --upstream")
        upstream = validate_upstream(upstream)
    elif webroot is not None:
        webroot = validate_webroot(str(webroot))
    else:
        raise typer.BadParameter(
            "必须提供 --webroot ./dist（静态） 或 --proxy --upstream URL（反代）"
        )

    dns_config = load_dns_config()
    if not dns_config:
        typer.echo("❌ 缺少 DNS 配置，请先执行: publish config dns", err=True)
        raise typer.Exit(code=1)
    ssh_config = load_ssh_config()
    if not ssh_config:
        typer.echo("❌ 缺少 SSH 配置，请先执行: publish config ssh", err=True)
        raise typer.Exit(code=1)

    dns_provider = get_dns_provider(dns_config)
    server_ip = ip or ssh_config.host

    pipe = Pipeline(f"deploy:{domain}")

    @pipe.on_step
    def _echo(step: Step):
        typer.echo(format_step(step))

    def _step_dns() -> Step:
        return action_dns_create_record(
            domain, server_ip, dns_provider=dns_provider, force=force
        )

    def _step_nginx() -> Step:
        return action_nginx_deploy(
            ssh_config, domain, webroot=webroot, upstream=upstream, with_ssl=ssl
        )

    def _step_ssl() -> Step:
        return action_ssl_request_cert(ssh_config, domain)

    pipe.add(_step_dns, name=f"dns:{domain}")
    pipe.add(_step_nginx, name=f"nginx:{domain}")
    if ssl:
        pipe.add(_step_ssl, name=f"ssl:{domain}")
    else:
        pipe.add(lambda: Step(name=f"ssl:{domain}", status="skipped", output="no-ssl"))

    success = pipe.run()
    typer.echo("")
    typer.echo(pipe.summary())
    status = PublishStatus.SUCCESS if success else PublishStatus.FAILED
    log_publish(domain, PublishOperation.DEPLOY, status, pipe.summary())
    icon = "🚀" if success else "⚠️"
    url_scheme = "https" if ssl and success else "http"
    typer.echo(f"{icon} 发布{'完成' if success else '（部分失败）'}: {url_scheme}://{domain}")
    if not success:
        raise typer.Exit(code=1)


# ── rollback (still inline because rollback is one-shot, no pipeline) ────

@app.command("rollback")
def rollback_cmd(subdomain: str = typer.Argument(..., help="目标子域名")):
    """回滚到上一版本."""
    from publish.nginx.deploy import rollback as nginx_rollback
    from publish.ssh.client import SshClient, SshConnectionError

    subdomain = validate_subdomain(subdomain)
    ssh_config = load_ssh_config()
    if not ssh_config:
        typer.echo("❌ 缺少 SSH 配置", err=True)
        raise typer.Exit(code=1)
    try:
        with SshClient(ssh_config) as ssh:
            timestamp = nginx_rollback(ssh, subdomain)
        typer.echo(f"↩️  已回滚: {subdomain} → {timestamp} 版本")
        log_publish(subdomain, PublishOperation.ROLLBACK, PublishStatus.SUCCESS, f"回滚到 {timestamp}")
    except SshConnectionError as e:
        typer.echo(f"❌ SSH 连接失败: {e}", err=True)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        typer.echo(f"❌ 回滚失败: {e}", err=True)
        log_publish(subdomain, PublishOperation.ROLLBACK, PublishStatus.FAILED, str(e))
        raise typer.Exit(code=1)


# ── cert / list (thin shims to commands/) ────────────────────────────────

@cert_app.command("status")
def _cert_status(subdomain: str = typer.Argument(..., help="子域名")):
    """查看子域名 SSL 证书状态."""
    cert_status(subdomain=subdomain)


@cert_app.command("renew")
def _cert_renew(subdomain: str = typer.Argument(..., help="子域名")):
    """手动强制续期证书."""
    cert_renew(subdomain=subdomain)


@app.command("list")
def list_cmd():
    """查看所有已发布子域名."""
    list_published_cmd()


if __name__ == "__main__":
    app()
