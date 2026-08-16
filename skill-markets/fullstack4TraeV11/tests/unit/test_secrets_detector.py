"""secrets-detector.py 单元测试(P3-4 NEW)。

覆盖维度:
  - AWS Access Key 检测
  - OpenAI API Key 检测
  - GitHub Token 检测
  - Generic credential (key=value) 检测 + 占位符排除
  - Authorization: Bearer 检测
  - Private Key Block 检测
  - JWT-like 检测
  - 中国大陆手机号 PII 检测
  - 身份证号 PII 检测
  - 邮箱 PII 检测
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "secrets-detector.py"
)


def _load_secrets_detector():
    spec = importlib.util.spec_from_file_location("secrets_detector", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _hits_for_text(text: str):
    """直接调用 scan_text() 跑单段文本。"""
    mod = _load_secrets_detector()
    patterns = mod._compile_patterns()
    return mod.scan_text(text, patterns)


# ============================================================================
# TestPatternCoverage — 每类 pattern 至少 1 PASS + 1 边界
# ============================================================================
class TestPatternCoverage:
    def test_aws_access_key_detected(self):
        """PASS:AWS Key 命中。"""
        text = "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF\n"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "aws-access-key" for h in hits), hits

    def test_aws_access_key_short_prefix_ignored(self):
        """边界:AKIA + 短字符(<16)→ 不命中。"""
        text = "FAKE_AKIA1234567890ABC\n"  # 14 chars after AKIA
        hits = _hits_for_text(text)
        # 这个可能被 aws-access-key 命中(因为[A-Z0-9]匹配范围可能宽松)
        # 实际上 AKIA1234567890ABC 是 14 chars — \b + {16} 不会匹配
        aws_hits = [h for h in hits if h["pattern_id"] == "aws-access-key"]
        assert aws_hits == [], f"过短不应命中,实际: {aws_hits}"

    def test_openai_api_key_detected(self):
        """PASS:sk- 开头 32 字符命中。"""
        text = "OPENAI_KEY=sk-abcdef1234567890abcdef1234567890ab\n"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "openai-api-key" for h in hits), hits

    def test_github_token_detected(self):
        """PASS:ghp_ + 36 字符命中。"""
        text = "GITHUB_TOKEN=ghp_abcdefghijklmnopqrstuvwxyz0123456789\n"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "github-token" for h in hits), hits

    def test_generic_credential_keyvalue_detected(self):
        """PASS:password = real_value 命中。"""
        text = 'config = {"password": "secret123"}'
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "generic-credential-keyvalue" for h in hits), hits

    def test_generic_credential_placeholder_excluded(self):
        """边界:password = xxx 占位符被排除。"""
        text = 'config = {"password": "xxx"}'
        hits = _hits_for_text(text)
        assert not any(h["pattern_id"] == "generic-credential-keyvalue" for h in hits), \
            f"占位符不应命中,实际: {hits}"

    def test_authorization_bearer_detected(self):
        """PASS:Authorization: Bearer + JWT-like 命中。"""
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\n"
        hits = _hits_for_text(text)
        # 至少 jwt-like 和 authorization-bearer 命中其一
        assert any(h["pattern_id"] in ("authorization-bearer", "jwt-like") for h in hits), hits

    def test_private_key_block_detected(self):
        """PASS:-----BEGIN PRIVATE KEY----- 命中。"""
        text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA..."
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "private-key-block" for h in hits), hits

    def test_jwt_like_detected(self):
        """PASS:JWT 形式(eyJ + base64 + . + base64 + . + base64)命中。"""
        text = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "jwt-like" for h in hits), hits

    def test_china_mobile_detected(self):
        """PASS:11 位中国大陆手机号命中。"""
        text = "user_phone = 13812345678"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "china-mobile-phone" for h in hits), hits

    def test_china_id_card_detected(self):
        """PASS:18 位身份证号命中。"""
        text = "id_card = 11010119900307881X"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "china-id-card" for h in hits), hits

    def test_email_pii_excludes_example(self):
        """边界:example.com 邮箱 → 不命中。"""
        text = "support email: admin@example.com"
        hits = _hits_for_text(text)
        assert not any(h["pattern_id"] == "email-pii" for h in hits), \
            f"example.com 应排除,实际: {hits}"

    def test_email_pii_real_domain_detected(self):
        """PASS:真实域名邮箱命中。"""
        text = "contact: alice.smith@company.com"
        hits = _hits_for_text(text)
        assert any(h["pattern_id"] == "email-pii" for h in hits), hits


# ============================================================================
# TestCLIIntegration — 真反例跑 CLI 验证
# ============================================================================
class TestCLIIntegration:
    def test_cli_fails_on_secrets_file(self, tmp_path):
        """真反例:tmp 造含 AKIA / Bearer / password 文件 → CLI exit 1。"""
        target = tmp_path / "leaked.txt"
        target.write_text(
            "# leaked creds\n"
            "AWS_ACCESS_KEY_ID=AKIA1234567890ABCDEF\n"
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c\n"
            "password = secret123abc\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH),
             "--file", str(target),
             "--json"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 1, f"期望 exit 1,实际 {result.returncode}"
        # JSON 含 hit_count > 0
        import json
        out = json.loads(result.stdout)
        assert out["hit_count"] >= 3, f"应至少 3 类命中,实际 {out['hit_count']}: {out}"