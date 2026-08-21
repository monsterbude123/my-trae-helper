"""SSH client wrapper over Paramiko."""

import os
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

from paramiko import SSHClient, AutoAddPolicy, SSHException, AuthenticationException

from publish.models import SshConfig


class SshConnectionError(Exception):
    """Raised when SSH connection fails."""


def _format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _progress_bar(transferred: int, total: int, width: int = 30) -> str:
    """Generate a simple progress bar string."""
    if total == 0:
        return ""
    ratio = min(transferred / total, 1.0)
    filled = int(width * ratio)
    bar = "█" * filled + "░" * (width - filled)
    pct = ratio * 100
    return f"[{bar}] {pct:5.1f}%  {_format_size(transferred)}/{_format_size(total)}"


class SshClient:
    """SSH client for remote command execution and file upload."""

    def __init__(self, config: SshConfig):
        self._config = config
        self._client: Optional[SSHClient] = None
        self._progress_enabled = True

    def connect(self) -> None:
        """Establish SSH connection."""
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            connect_kwargs = {
                "hostname": self._config.host,
                "port": self._config.port,
                "username": self._config.user,
                "timeout": 30,
            }
            if self._config.key_path:
                connect_kwargs["key_filename"] = str(self._config.key_path)
            if self._config.password:
                connect_kwargs["password"] = self._config.password
            client.connect(**connect_kwargs)
            self._client = client
        except AuthenticationException as e:
            raise SshConnectionError(f"SSH 认证失败: {e}") from e
        except SSHException as e:
            raise SshConnectionError(f"SSH 连接失败: {e}") from e
        except OSError as e:
            raise SshConnectionError(f"SSH 连接超时或主机不可达: {e}") from e

    def exec_command(self, command: str) -> tuple[int, str, str]:
        """Execute a command on the remote host. Returns (exit_code, stdout, stderr)."""
        if not self._client:
            raise SshConnectionError("SSH 未连接，请先调用 connect()")
        _, stdout, stderr = self._client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return exit_code, stdout.read().decode(), stderr.read().decode()

    def upload_file(self, local_path: Path, remote_path: str) -> None:
        """Upload a file via SFTP with progress display."""
        if not self._client:
            raise SshConnectionError("SSH 未连接，请先调用 connect()")
        sftp = self._client.open_sftp()
        try:
            file_size = local_path.stat().st_size
            if self._progress_enabled:
                last = [0]

                def _cb(transferred: int, total: int):
                    if transferred - last[0] >= total // 20 or transferred == total:
                        bar = _progress_bar(transferred, total)
                        sys.stdout.write(f"\r  {local_path.name:40s} {bar}")
                        sys.stdout.flush()
                        last[0] = transferred

                sftp.put(str(local_path), remote_path, callback=_cb)
                sys.stdout.write("\n")
                sys.stdout.flush()
            else:
                sftp.put(str(local_path), remote_path)
        finally:
            sftp.close()

    def _collect_files(self, local_dir: Path) -> list[tuple[Path, int]]:
        """Collect all files with sizes for progress tracking."""
        files = []
        for item in sorted(local_dir.rglob("*")):
            if item.is_file():
                files.append((item, item.stat().st_size))
        return files

    def upload_directory(self, local_dir: Path, remote_dir: str) -> None:
        """Upload an entire directory via SFTP recursively with progress display."""
        if not self._client:
            raise SshConnectionError("SSH 未连接，请先调用 connect()")
        sftp = self._client.open_sftp()
        try:
            # Ensure remote dir exists
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                sftp.mkdir(remote_dir)

            # Collect all files first for progress tracking
            all_files = self._collect_files(local_dir)
            total_bytes = sum(s for _, s in all_files)
            uploaded = [0]  # mutable counter for closure

            print(f"  📁 共 {len(all_files)} 个文件，总计 {_format_size(total_bytes)}")

            for local_path, file_size in all_files:
                rel = local_path.relative_to(local_dir)
                remote_item = f"{remote_dir}/{rel}".replace("\\", "/")

                # Ensure parent directories exist
                remote_parent = os.path.dirname(remote_item).replace("\\", "/")
                self._ensure_remote_dir(sftp, remote_parent)

                # Upload with progress
                if self._progress_enabled and file_size > 0:
                    last = [0]

                    def _cb(transferred: int, total: int):
                        current_total = uploaded[0] + transferred
                        if transferred - last[0] >= total // 20 or transferred == total:
                            bar = _progress_bar(current_total, total_bytes)
                            name = local_path.name
                            if len(name) > 35:
                                name = name[:32] + "..."
                            sys.stdout.write(f"\r  {name:35s} {bar}")
                            sys.stdout.flush()
                            last[0] = transferred

                    sftp.put(str(local_path), remote_item, callback=_cb)
                else:
                    sftp.put(str(local_path), remote_item)

                uploaded[0] += file_size

            sys.stdout.write("\n")
            sys.stdout.flush()
        finally:
            sftp.close()

    def upload_tarball(self, local_dir: Path, remote_dir: str) -> None:
        """Pack directory as tar.gz, upload single file with progress, extract remotely."""
        if not self._client:
            raise SshConnectionError("SSH 未连接，请先调用 connect()")

        # Step 1: Create tar.gz locally
        print("  📦 打包中...")
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tarball_path = tmp.name

        try:
            with tarfile.open(tarball_path, "w:gz") as tar:
                tar.add(str(local_dir), arcname=".")

            tarball_size = os.path.getsize(tarball_path)
            print(f"  📦 打包完成: {_format_size(tarball_size)}")

            # Step 2: Upload the tarball with progress
            remote_tarball = f"/tmp/_deploy_{os.path.basename(tarball_path)}"
            sftp = self._client.open_sftp()
            try:
                if self._progress_enabled:
                    last = [0]

                    def _cb(transferred: int, total: int):
                        if transferred - last[0] >= total // 20 or transferred == total:
                            bar = _progress_bar(transferred, total)
                            sys.stdout.write(f"\r  📤 上传 {bar}")
                            sys.stdout.flush()
                            last[0] = transferred

                    sftp.put(tarball_path, remote_tarball, callback=_cb)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                else:
                    sftp.put(tarball_path, remote_tarball)
            finally:
                sftp.close()

            # Step 3: Extract remotely
            print(f"  📂 解压到 {remote_dir} ...")
            self.exec_command(f"mkdir -p {remote_dir}")
            exit_code, stdout, stderr = self.exec_command(
                f"tar -xzf {remote_tarball} -C {remote_dir} --strip-components=0 2>&1"
            )
            if exit_code != 0:
                raise RuntimeError(f"远程解压失败: {stderr}")

            # Step 4: Cleanup
            self.exec_command(f"rm -f {remote_tarball}")
            print("  ✅ 解压完成")

        finally:
            os.unlink(tarball_path)

    def _ensure_remote_dir(self, sftp, remote_dir: str) -> None:
        """Ensure remote directory exists, creating parents if needed."""
        parts = remote_dir.strip("/").split("/")
        current = ""
        for part in parts:
            current += "/" + part
            try:
                sftp.stat(current)
            except FileNotFoundError:
                sftp.mkdir(current)

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()
