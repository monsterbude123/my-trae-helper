"""Validation rules for publish CLI."""

import re
from pathlib import Path
from publish.models import DnsProvider, SshConfig

# VR-001
SUBDOMAIN_RE = re.compile(
    r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?\.[a-z][a-z0-9-]*\.[a-z]{2,}$"
)

# VR-002
IPV4_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

# VR-006
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def validate_subdomain(value: str) -> str:
    """VR-001: Validate subdomain format."""
    if len(value) > 253:
        raise ValueError(f"子域名过长（{len(value)} > 253 字符）: {value}")
    if value.startswith(("http://", "https://")):
        raise ValueError(f"子域名不得包含协议头: {value}")
    if not SUBDOMAIN_RE.match(value):
        raise ValueError(f"子域名格式无效: {value}")
    return value


def validate_ipv4(value: str) -> str:
    """VR-002: Validate IPv4 address."""
    if not IPV4_RE.match(value):
        raise ValueError(f"IPv4 格式无效: {value}")
    parts = value.split(".")
    if any(int(p) > 255 for p in parts):
        raise ValueError(f"IPv4 段超出 0-255 范围: {value}")
    return value


def validate_webroot(value: str) -> Path:
    """VR-003: Validate webroot path exists and has files."""
    path = Path(value).resolve()
    if not path.exists():
        raise ValueError(f"Webroot 路径不存在: {path}")
    if not path.is_dir():
        raise ValueError(f"Webroot 必须是目录: {path}")
    if not any(path.iterdir()):
        raise ValueError(f"Webroot 目录为空: {path}")
    return path


def validate_ssh_config(config: SshConfig) -> None:
    """VR-004: Validate SSH auth (key_path or password)."""
    if not config.key_path and not config.password:
        raise ValueError("SSH 认证至少需要 key_path 或 password 之一")
    if config.key_path and not Path(config.key_path).exists():
        raise ValueError(f"SSH 密钥文件不存在: {config.key_path}")


def validate_dns_provider(provider: str) -> DnsProvider:
    """VR-005: Validate DNS provider is one of supported."""
    try:
        return DnsProvider(provider)
    except ValueError:
        raise ValueError(f"不支持的 DNS 提供商: {provider}，可选: cloudflare, aliyun, dnspod")


def validate_publish_name(value: str) -> str:
    """VR-006: Validate publish name."""
    if len(value) > 63:
        raise ValueError(f"发布名称过长（{len(value)} > 63 字符）: {value}")
    if not NAME_RE.match(value):
        raise ValueError(f"发布名称格式无效: {value}（只允许小写字母、数字、连字符）")
    return value


# VR-007: Reverse-proxy upstream URL (http(s)://host:port[/path])
UPSTREAM_RE = re.compile(
    r"^https?://[A-Za-z0-9._-]+(?::\d{1,5})?(?:/[^\s]*)?$"
)


def validate_upstream(value: str) -> str:
    """VR-007: Validate reverse-proxy upstream URL.

    Examples:
      - http://127.0.0.1:8088
      - http://127.0.0.1:8088/api
      - http://app-container
      - https://backend.internal:8443
    Rejects: missing scheme, malformed port, whitespace.
    """
    v = value.strip()
    if not v:
        raise ValueError("upstream URL 不能为空")
    if v.startswith(("http://", "https://")) is False:
        raise ValueError(f"upstream URL 必须以 http:// 或 https:// 开头: {v}")
    if " " in v or "\t" in v or "\n" in v:
        raise ValueError(f"upstream URL 含非法空白字符: {v!r}")
    if not UPSTREAM_RE.match(v):
        raise ValueError(f"upstream URL 格式无效: {v}")
    # port range guard
    m = re.match(r"^https?://[^:]+(?::(\d{1,5}))?", v)
    if m and m.group(1):
        port = int(m.group(1))
        if not (1 <= port <= 65535):
            raise ValueError(f"upstream 端口超出 1-65535: {port}")
    return v
