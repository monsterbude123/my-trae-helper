"""Configuration store — read/write ~/.publish/config.yaml + .env fallback."""

import os
from pathlib import Path
from typing import Optional

import yaml

from publish.models import SshConfig, DnsConfig, DnsProvider

DEFAULT_CONFIG_DIR = Path.home() / ".publish"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.yaml"
ENV_FILE = Path(".env")


def _parse_env_file(path: Path) -> dict:
    """Minimal .env parser: KEY=VALUE, ignore comments and blank lines.

    VR-008 (2026-08-20): strip matched wrapping quotes ('\"' or single) from
    values so PowerShell-written .env entries like SSH_KEY_PATH="C:\\..." don't
    blow up paramiko with OSError [Errno 22]. Skips unmatched quotes (path
    may legitimately contain a single \").
    """
    env = {}
    if not path.exists():
        return env
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            value = value.strip()
            # VR-008 strip wrapping quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            env[key.strip()] = value
    return env


def _get_env_value(key: str) -> Optional[str]:
    """Get value from .env file in current dir, fallback to os.environ."""
    env = _parse_env_file(ENV_FILE)
    if key in env and env[key]:
        return env[key]
    return os.environ.get(key)


def _ensure_dir() -> None:
    DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load config from ~/.publish/config.yaml. Returns empty dict if not exists.

    Note: .env is NOT auto-loaded into YAML config — it only fills missing values
    when loading SshConfig/DnsConfig via dedicated helpers.
    """
    if not DEFAULT_CONFIG_PATH.exists():
        return {}
    with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def save_config(data: dict) -> None:
    """Save config to ~/.publish/config.yaml."""
    _ensure_dir()
    with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)
    # Set secure permissions (Unix only)
    if os.name != "nt":
        os.chmod(DEFAULT_CONFIG_PATH, 0o600)


def load_ssh_config() -> Optional[SshConfig]:
    """Load SSH config from YAML, fallback to .env.

    Priority: ~/.publish/config.yaml > .env (project root) > os.environ
    """
    data = load_config().get("ssh")
    host = (data or {}).get("host") or _get_env_value("SSH_HOST")
    user = (data or {}).get("user") or _get_env_value("SSH_USER")
    if not host or not user:
        return None
    port_str = (data or {}).get("port") or _get_env_value("SSH_PORT")
    key_path = (data or {}).get("key_path") or _get_env_value("SSH_KEY_PATH")
    password = (data or {}).get("password") or _get_env_value("SSH_PASSWORD")
    return SshConfig(
        host=host,
        user=user,
        port=int(port_str) if port_str else 22,
        key_path=Path(key_path) if key_path else None,
        password=password if password else None,
    )


def save_ssh_config(config: SshConfig) -> None:
    """Save SSH config to file."""
    data = load_config()
    data["ssh"] = {
        "host": config.host,
        "user": config.user,
        "port": config.port,
    }
    if config.key_path:
        data["ssh"]["key_path"] = str(config.key_path)
    if config.password:
        data["ssh"]["password"] = config.password
    save_config(data)


def load_dns_config() -> Optional[DnsConfig]:
    """Load DNS config from YAML, fallback to .env (only for aliyun fields).

    Priority: ~/.publish/config.yaml > .env (project root) > os.environ
    """
    data = load_config().get("dns")
    if not data:
        return None
    provider = DnsProvider(data["provider"])

    # Fallback fields from .env (only for aliyun currently; cloudflare/dnspod need interactive)
    api_token = data.get("api_token") or _get_env_value("CLOUDFLARE_API_TOKEN")
    zone_id = data.get("zone_id") or _get_env_value("CLOUDFLARE_ZONE_ID")
    domain = data.get("domain") or _get_env_value("ALIYUN_DOMAIN") or _get_env_value("DNSPOD_DOMAIN")
    access_key_id = data.get("access_key_id") or _get_env_value("ALIYUN_ACCESS_KEY_ID")
    access_key_secret = data.get("access_key_secret") or _get_env_value("ALIYUN_ACCESS_KEY_SECRET")
    secret_id = data.get("secret_id") or _get_env_value("DNSPOD_SECRET_ID")
    secret_key = data.get("secret_key") or _get_env_value("DNSPOD_SECRET_KEY")

    return DnsConfig(
        provider=provider,
        api_token=api_token or "",
        zone_id=zone_id,
        domain=domain,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        secret_id=secret_id,
        secret_key=secret_key,
    )


def save_dns_config(config: DnsConfig) -> None:
    """Save DNS config to file."""
    data = load_config()
    dns_data = {"provider": config.provider.value}
    if config.api_token:
        dns_data["api_token"] = config.api_token
    if config.zone_id:
        dns_data["zone_id"] = config.zone_id
    if config.domain:
        dns_data["domain"] = config.domain
    if config.access_key_id:
        dns_data["access_key_id"] = config.access_key_id
    if config.access_key_secret:
        dns_data["access_key_secret"] = config.access_key_secret
    if config.secret_id:
        dns_data["secret_id"] = config.secret_id
    if config.secret_key:
        dns_data["secret_key"] = config.secret_key
    data["dns"] = dns_data
    save_config(data)
