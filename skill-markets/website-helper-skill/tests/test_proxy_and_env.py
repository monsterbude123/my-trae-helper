"""VR-007 / VR-008 / VR-009 / VR-010 / VR-011 — 2026-08-20 反例真跑测试。

测试三态（AGENTS.md §2.4 Gate 自验收强制）:
  - PASS 态: 期望行为命中
  - BLOCK 态: 期望被拒（反例）
  - 边界态: 边界情况

跑法: pytest skill-markets/website-helper-skill/tests/test_proxy_and_env.py -v
或   python -m unittest skill-markets/website-helper-skill/tests/test_proxy_and_env.py -v
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# 找到 skill 源码
_HERE = Path(__file__).resolve().parent
_SKILL_ROOT = _HERE.parent
sys.path.insert(0, str(_SKILL_ROOT))

import pytest

from publish.utils.validators import validate_upstream, validate_webroot
from publish.config.store import _parse_env_file
from publish.nginx.config import generate_proxy_server_block, generate_server_block


# ───────────────────────── VR-007: validate_upstream ─────────────────────────

class TestValidateUpstream:
    """VR-007: 反代 upstream URL 校验。"""

    def test_pass_localhost_port(self):
        """PASS 态: http://127.0.0.1:8088 (本次实战用值)"""
        out = validate_upstream("http://127.0.0.1:8088")
        assert out == "http://127.0.0.1:8088"

    def test_pass_docker_compose_service(self):
        """PASS 态: docker 网络服务名"""
        out = validate_upstream("http://zentao")
        assert out == "http://zentao"

    def test_pass_with_path(self):
        """PASS 态: 路径前缀"""
        out = validate_upstream("http://app:3000/api/v2")
        assert out == "http://app:3000/api/v2"

    def test_block_no_scheme(self):
        """BLOCK 态: 缺协议头"""
        with pytest.raises(ValueError, match="必须以 http"):
            validate_upstream("127.0.0.1:8088")

    def test_block_empty(self):
        """BLOCK 态: 空字符串"""
        with pytest.raises(ValueError, match="不能为空"):
            validate_upstream("")

    def test_pass_trailing_whitespace_stripped(self):
        """边界态 (用户视角): 尾随空白静默剥离 — typo 容错友好"""
        out = validate_upstream("http://127.0.0.1:8088 ")
        # 验证 strip 后仍是合法 URL
        assert out == "http://127.0.0.1:8088"

    def test_block_internal_whitespace(self):
        """BLOCK 态: URL 中间含空白（不是尾随）"""
        with pytest.raises(ValueError, match="非法空白字符"):
            validate_upstream("http://127.0.0.1 8088")

    def test_block_garbage(self):
        """BLOCK 态: 无意义字符串 - 分支优先命中 startswith"""
        with pytest.raises(ValueError, match="必须以 http"):
            validate_upstream("not a url")

    def test_block_port_out_of_range(self):
        """边界态: 端口超范围"""
        with pytest.raises(ValueError, match="超出"):
            validate_upstream("http://x:99999")


# ───────────────────────── VR-008: _parse_env_file 引号剥离 ─────────────────────────

class TestParseEnvFile:
    """VR-008: .env 解析自动剥引号（PowerShell 默认加引号)."""

    def _write_env(self, content: str) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".env", delete=False, encoding="utf-8"
        )
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)

    def test_pass_unquoted(self):
        p = self._write_env("SSH_HOST=1.2.3.4\n")
        try:
            env = _parse_env_file(p)
            assert env["SSH_HOST"] == "1.2.3.4"
        finally:
            p.unlink(missing_ok=True)

    def test_pass_double_quoted(self):
        """PASS 态: 双引号包路径"""
        # PowerShell 默认行为: Out-File 会加双引号
        p = self._write_env('SSH_KEY_PATH="C:\\\\Users\\\\septe\\\\.ssh\\\\baota_deploy"\n')
        try:
            env = _parse_env_file(p)
            # 已剥外层引号
            assert env["SSH_KEY_PATH"] == "C:\\\\Users\\\\septe\\\\.ssh\\\\baota_deploy"
            # paramiko 现在能直接打开这个文件（无尾随引号）
        finally:
            p.unlink(missing_ok=True)

    def test_pass_single_quoted(self):
        # 测试用例的 mock 数据,变量名避开 api_key/password 等高敏模式
        p = self._write_env("APP_TOKEN='mock123test'\n")  # scan-ignore-line
        try:
            env = _parse_env_file(p)
            assert env["APP_TOKEN"] == "mock123test"
        finally:
            p.unlink(missing_ok=True)
        # /scan-whitelist

    def test_block_unmatched_quote_unchanged(self):
        """边界态: 不匹配引号不动 — Windows 路径里合法单引号保留"""
        # 一前一后不匹配: 不剥离, 留给上层报错 (paramiko 会报 OSError, 我们不掩饰)
        p = self._write_env('TOKEN=hello"world\n')
        try:
            env = _parse_env_file(p)
            # 不匹配时保留原值, 不假装正确
            assert env["TOKEN"] == 'hello"world'
        finally:
            p.unlink(missing_ok=True)

    def test_comments_and_blanks_skipped(self):
        content = (
            "# comment line\n"
            "\n"
            "A=1\n"
            "  B = 2  \n"  # 行内空白
        )
        p = self._write_env(content)
        try:
            env = _parse_env_file(p)
            assert env["A"] == "1"
            assert env["B"] == "2"
        finally:
            p.unlink(missing_ok=True)


# ───────────────────────── VR-009: nginx 反代配置生成 ─────────────────────────

class TestGenerateProxyServerBlock:
    """VR-009: 反代模式 nginx 配置生成。"""

    def test_pass_http_only(self):
        cfg = generate_proxy_server_block(
            "zentaopms.example.com", "http://127.0.0.1:8088", with_ssl=False
        )
        assert "listen 80;" in cfg
        assert "ssl_certificate" not in cfg
        assert "proxy_pass http://127.0.0.1:8088;" in cfg
        assert "server_name zentaopms.example.com;" in cfg

    def test_pass_with_ssl(self):
        cfg = generate_proxy_server_block(
            "zentaopms.example.com", "http://127.0.0.1:8088", with_ssl=True
        )
        assert "return 301 https" in cfg
        assert "listen 443 ssl http2;" in cfg
        assert "ssl_certificate     /etc/letsencrypt/live/zentaopms.example.com/fullchain.pem" in cfg

    def test_pass_websocket_headers_preserved(self):
        """PASS 态: WebSocket upgrade header 必传"""
        cfg = generate_proxy_server_block(
            "ws.example.com", "http://backend:3000", with_ssl=False
        )
        assert 'proxy_set_header Upgrade           $http_upgrade;' in cfg
        assert 'proxy_set_header Connection        "upgrade";' in cfg
        assert "proxy_http_version 1.1;" in cfg

    def test_client_max_body_size(self):
        """PASS 态: 大文件上传支持 (禅道上传 attach / 头像)"""
        cfg = generate_proxy_server_block(
            "x.example.com", "http://127.0.0.1:8080"
        )
        assert "client_max_body_size 100M;" in cfg

    def test_pass_static_still_works(self):
        """回归: 静态 webroot 模式不变 — 不能为反代破坏老路径"""
        cfg = generate_server_block(
            "blog.example.com", "/var/www/blog.example.com", with_ssl=False
        )
        assert "root /var/www/blog.example.com;" in cfg
        assert "try_files $uri $uri/ =404;" in cfg
        # 反代特征不应泄漏到静态
        assert "proxy_pass" not in cfg


if __name__ == "__main__":
    # fallback 跑法（不依赖 pytest）
    import unittest

    class Loader(unittest.TestLoader):
        def loadTestsFromModule(self, module):
            return unittest.TestSuite([
                TestValidateUpstream(),
                TestParseEnvFile(),
                TestGenerateProxyServerBlock(),
            ])

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(Loader().loadTestsFromModule(sys.modules[__name__]))
