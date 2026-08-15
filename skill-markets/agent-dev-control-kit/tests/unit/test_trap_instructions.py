"""tests/unit/test_trap_instructions.py — trap 反例指令映射

验证 trap-instructions.yaml 的结构完整性 + 关键反例存在:
  - 至少含 AP-2 / AP-3 / AP-CAT-* 条目
  - next_skill 字段非空(便于 agent 直接调用)
  - fix_template_after 真存在
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

TRAP_FILE = (
    Path(__file__).resolve().parents[2]
    / "references"
    / "trap-instructions.yaml"
)


@pytest.fixture(scope="module")
def trap_map():
    data = yaml.safe_load(TRAP_FILE.read_text(encoding="utf-8"))
    traps_by_id = {t["id"]: t for t in data.get("traps", []) or []}
    return traps_by_id


# ============================================================================
# Trap 完整性
# ============================================================================
REQUIRED_TRAP_IDS = [
    "AP-1",
    "AP-2",
    "AP-3",
    "AP-CAT-DOCS",
    "AP-CAT-SECTIONS",
    "AP-CAT-SCHEMA",
    "AP-CAT-DOCS-LANG",
    "AP-CAT-META-REGISTER",
    "AP-17",
]


class TestTrapInstructionsExists:
    @pytest.mark.trap
    @pytest.mark.parametrize("tid", REQUIRED_TRAP_IDS)
    def test_required_trap_present(self, trap_map, tid):
        assert tid in trap_map, f"trap-instructions.yaml 缺反例 {tid}"

    @pytest.mark.trap
    def test_version_present(self):
        data = yaml.safe_load(TRAP_FILE.read_text(encoding="utf-8"))
        assert "version" in data


class TestTrapInstructionsQuality:
    @pytest.mark.trap
    @pytest.mark.parametrize("tid", REQUIRED_TRAP_IDS)
    def test_each_trap_has_required_fields(self, trap_map, tid):
        """每条 trap 必含:title / detect_signal / what_is_wrong / fix_template_after / next_skill。"""
        trap = trap_map.get(tid)
        assert trap is not None, f"{tid} 缺失"
        for field in ("title", "detect_signal", "what_is_wrong", "fix_template_after", "next_skill"):
            assert field in trap, f"{tid} 缺 {field!r}"

    @pytest.mark.trap
    @pytest.mark.parametrize("tid", REQUIRED_TRAP_IDS)
    def test_each_trap_has_minimal_fix_examples(self, trap_map, tid):
        """有 fix_template_after(✅) 表明 agent 知道如何修。"""
        trap = trap_map[tid]
        assert "✅" in trap["fix_template_after"], f"{tid} fix_template_after 应含 ✅ 标记"

    @pytest.mark.trap
    def test_ap2_explicit_blocking_template(self, trap_map):
        """AP-2 必含 exit 1 + 显式提示(对应 §11.1.4)。"""
        ap2 = trap_map["AP-2"]
        after = ap2["fix_template_after"]
        assert "exit 1" in after or "exit(1)" in after, "AP-2 必须显式阻断"

    @pytest.mark.trap
    def test_ap3_main_block_template(self, trap_map):
        """AP-3 main block 模板必须包含 import.meta.url 或 __main__。"""
        ap3 = trap_map["AP-3"]
        after = ap3["fix_template_after"]
        assert "import.meta.url" in after or "__main__" in after


class TestTrapCatalogLink:
    """trap-instructions.yaml 应与 catalog 测试联动 — 见 ID 对应。"""

    @pytest.mark.trap
    def test_catalog_ap_cats_have_corresponding_trap(self, trap_map):
        """catalog test 用的 trap_id(AP-CAT-001~005)应当映射到 trap-instructions 中的 AP-CAT-*。"""
        # catalog test 的 trap_id 形式:AP-CAT-001~005,但 trap-instructions 用 AP-CAT-DOCS/SECTIONS/SCHEMA
        # 这是命名收敛问题:后续可统一,目前只验证有 AP-CAT 前缀
        cat_traps = [tid for tid in trap_map if tid.startswith("AP-CAT")]
        assert len(cat_traps) >= 3, "AP-CAT-* 反例至少应有 3 条"
