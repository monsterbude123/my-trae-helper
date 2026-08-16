"""proactive-scan.py scan_reason_fabrication 已知误报修复测试(P3-3)。

覆盖维度:
  - PASS:报告内"反例说明段"引用禁词 → 上下文窗口关键词命中 → 跳过(不误报)
  - PASS:docs/specs/_invalidated/ 路径下文件引用禁词 → 跳过(不误报)
  - PASS:docs/reports/rot-scan-2026-08-16.md 含判定偏差 → 跳过(已存在的目录白名单)
  - FAIL:真实使用禁词的报告 → 仍 FAIL
  - FAIL:不带上下文关键词的禁词 → 仍 FAIL
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "proactive-scan.py"
)


def _load_proactive_scan():
    spec = importlib.util.spec_from_file_location("proactive_scan", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ============================================================================
# TestFalsePositiveFixes — P3-3 已知误报场景
# ============================================================================
class TestFalsePositiveFixes:
    """临时 tmp_path 造测试场景,避免污染真实项目。"""

    def test_docs_specs_invalidated_skipped(self, tmp_path):
        """PASS:docs/specs/_invalidated/ 路径下文件含禁词 → 跳过。"""
        mod = _load_proactive_scan()
        inv_dir = tmp_path / "docs/specs/_invalidated/2026-08-15-old-spec"
        inv_dir.mkdir(parents=True)
        (inv_dir / "spec.md").write_text(
            "归档历史 spec,引用禁词 '理解偏差' / '权衡取舍' — "
            "这是 V11 缺漏 3 的反例说明段",
            encoding="utf-8",
        )
        ok, msg = mod.scan_reason_fabrication(tmp_path)
        assert ok is True, f"docs/specs/_invalidated/ 不应被误报,实际: {msg}"

    def test_context_keyword_v11_gap_skipped(self, tmp_path):
        """PASS:文件含'V11 缺漏'上下文关键词 + 禁词 → 跳过。"""
        mod = _load_proactive_scan()
        # 在常规 docs/ 下放文件,引用"反例:reason-fabrication 不看上下文"
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs/notes.md").write_text(
            "# V11 缺漏 3 反例说明段\n\n"
            "现象:报告内引用 '理解偏差' / '权衡取舍' 等禁词本身 → "
            "proactive-scan 不应误判这是真实理由\n",
            encoding="utf-8",
        )
        ok, msg = mod.scan_reason_fabrication(tmp_path)
        assert ok is True, f"含 V11 缺漏 / 反例说明 关键词应跳过,实际: {msg}"

    def test_reports_dir_with_keyword_skipped(self, tmp_path):
        """PASS:docs/reports/rot-scan-*.md 含 '判定偏差' + 上下文关键词 → 跳过。"""
        mod = _load_proactive_scan()
        rep_dir = tmp_path / "docs/reports"
        rep_dir.mkdir(parents=True)
        (rep_dir / "rot-scan-2026-08-16.md").write_text(
            "# Rot Scan Report\n\n"
            "## V11 缺漏误报说明\n\n"
            "本周新增误报 1 条: '判定偏差' 在 bug-hunt 报告被命中 — "
            "已加入上下文窗口白名单\n",
            encoding="utf-8",
        )
        ok, msg = mod.scan_reason_fabrication(tmp_path)
        assert ok is True, f"含 V11 缺漏 / 误报说明关键词应跳过,实际: {msg}"

    def test_real_usage_still_fails(self, tmp_path):
        """FAIL:不带上下文关键词的真实禁词使用 → 仍 FAIL。"""
        mod = _load_proactive_scan()
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs/real-bad-report.md").write_text(
            "# 实施报告\n\n"
            "今天又遇到理解偏差问题 — 用户反馈与产品设计目标存在偏差,"
            "团队协作出现概念漂移,需要重新对齐。\n",
            encoding="utf-8",
        )
        ok, msg = mod.scan_reason_fabrication(tmp_path)
        assert ok is False, "真实使用禁词应 FAIL"
        assert "real-bad-report" in msg, msg

    def test_bare_keyword_far_from_context_skipped_by_path(self, tmp_path):
        """边界:含上下文关键词("反例说明")+ 不带具体禁用陈述 → 跳过。"""
        mod = _load_proactive_scan()
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs/clean-report.md").write_text(
            "# 报告\n\n反例说明段:文中'理解偏差'用于说明示例,不构成真实理由使用\n",
            encoding="utf-8",
        )
        ok, msg = mod.scan_reason_fabrication(tmp_path)
        assert ok is True, f"含'反例说明'上下文关键词应跳过,实际: {msg}"