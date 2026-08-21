"""Domain models for publish CLI."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DnsProvider(str, Enum):
    CLOUDFLARE = "cloudflare"
    ALIYUN = "aliyun"
    DNSPOD = "dnspod"


class PublishOperation(str, Enum):
    DEPLOY = "deploy"
    ROLLBACK = "rollback"
    RENEW = "renew"


class PublishStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class CertStatus(str, Enum):
    VALID = "valid"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    ABSENT = "absent"


@dataclass
class SshConfig:
    host: str
    user: str
    port: int = 22
    key_path: Optional[Path] = None
    password: Optional[str] = field(default=None, repr=False)


@dataclass
class DnsConfig:
    provider: DnsProvider
    api_token: str = field(repr=False)
    zone_id: Optional[str] = None
    domain: Optional[str] = None
    # 阿里云/DNSPod 专用
    access_key_id: Optional[str] = field(default=None, repr=False)
    access_key_secret: Optional[str] = field(default=None, repr=False)
    secret_id: Optional[str] = field(default=None, repr=False)
    secret_key: Optional[str] = field(default=None, repr=False)


@dataclass
class DeployConfig:
    subdomain: str
    webroot: Path
    server_ip: Optional[str] = None
    enable_ssl: bool = True
    force: bool = False


@dataclass
class NginxBackup:
    subdomain: str
    timestamp: str
    config_path: str
    webroot_path: str


@dataclass
class PublishRecord:
    timestamp: str
    subdomain: str
    operation: PublishOperation
    status: PublishStatus
    detail: str = ""

    def to_markdown_row(self) -> str:
        status_icon = {"success": "✅", "partial": "⚠️", "failed": "❌"}
        icon = status_icon.get(self.status.value, "?")
        return f"| {self.timestamp} | {self.subdomain} | {self.operation.value} | {icon} {self.status.value} |"
