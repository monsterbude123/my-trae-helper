"""validate-gate-config.py 反例单元测试

每个用例对应 references/trap-instructions.yaml V11-T* 反例 + Gate 自验收铁律。
覆盖 dimensions:
  - G1 顶层 JSON 非法 / 缺 levels
  - G2 档位缺必填字段
  - G3 checks / gates 结构非法
  - G4 timeout / blocking / stage 非法
  - G5 缺档位 WARN（不阻断）
  - PASS 态:内置 gate-config.json 应 exit 0
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# ----------------------------------------------------------------------
# Helper — 构造 gate-config.json
# ----------------------------------------------------------------------
def _write_config(tmp_path: Path, data) -> Path:
    p = tmp_path / "gate-config.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


def _valid_levels() -> dict:
    """一份合法 levels 样本。"""
    return {
        level: {
            "description": f"{level} desc",
            "stage": {
                "L1": "1/spec",
                "L2": "3.5/real-verify",
                "L3": "2/contract,4/review,4.5/rot-scan",
                "L4": "5/accept",
            }[level],
            "host": {
                "L1": "husky-pre-commit",
                "L2": "husky-pre-push",
                "L3": "github-actions",
                "L4": "github-actions",
            }[level],
            "checks": ["lint", "test:unit"],
            "gates": ["stage-contract"] if level == "L3" else [],
            "timeout_seconds": 120,
            "blocking": True,
        }
        for level in ["L1", "L2", "L3", "L4"]
    }


# ============================================================================
# TestLoadConfig — G1 层
# ============================================================================
class TestLoadConfig:
    def test_missing_file(self, validate_gate_config, tmp_path):
        data, vulns = validate_gate_config.load_config(tmp_path / "nope.json")
        assert data is None
        codes = [v["code"] for v in vulns]
        assert "G1-GATE-CONFIG-MISSING" in codes

    @pytest.mark.trap
    def test_invalid_json(self, validate_gate_config, tmp_path):
        """G1 反例固化:非法 JSON → HIGH。"""
        p = tmp_path / "gate-config.json"
        p.write_text("{ not json !!!", encoding="utf-8")
        data, vulns = validate_gate_config.load_config(p)
        assert data is None
        codes = [v["code"] for v in vulns]
        assert "G1-GATE-CONFIG-INVALID-JSON" in codes
        assert any(v["severity"] == "HIGH" for v in vulns)

    def test_valid_json_returns_data(self, validate_gate_config, tmp_path):
        p = _write_config(tmp_path, {"levels": _valid_levels()})
        data, vulns = validate_gate_config.load_config(p)
        assert data is not None
        assert vulns == []


# ============================================================================
# TestValidateLevel — G2/G3/G4 层
# ============================================================================
class TestValidateLevel:
    def test_level_not_dict(self, validate_gate_config):
        vulns = validate_gate_config.validate_level("L1", "oops")
        codes = [v["code"] for v in vulns]
        assert "G2-LEVEL-NOT-DICT" in codes

    @pytest.mark.trap
    def test_missing_required_field(self, validate_gate_config):
        """G2 反例固化:缺必填字段 → HIGH。"""
        vulns = validate_gate_config.validate_level("L1", {"description": "x"})
        codes = [v["code"] for v in vulns]
        assert "G2-LEVEL-MISSING-FIELD" in codes
        assert any(v["severity"] == "HIGH" for v in vulns)

    @pytest.mark.trap
    def test_checks_not_list(self, validate_gate_config):
        """G3 反例固化:checks 非 list → HIGH。"""
        vulns = validate_gate_config.validate_level("L1", {"checks": "lint"})
        assert "G3-CHECKS-NOT-LIST" in [v["code"] for v in vulns]

    @pytest.mark.trap
    def test_checks_empty_string(self, validate_gate_config):
        """G3 反例固化:checks 含空字符串 → HIGH。"""
        vulns = validate_gate_config.validate_level("L1", {"checks": [""]})
        assert "G3-CHECKS-NOT-STR" in [v["code"] for v in vulns]

    @pytest.mark.trap
    def test_timeout_invalid(self, validate_gate_config):
        """G4 反例固化:timeout_seconds 非正 int → HIGH。"""
        for bad in [0, -5, "120", 2.5, True]:
            vulns = validate_gate_config.validate_level("L1", {"timeout_seconds": bad})
            assert "G4-TIMEOUT-INVALID" in [v["code"] for v in vulns], f"bad={bad!r}"

    @pytest.mark.trap
    def test_blocking_invalid(self, validate_gate_config):
        """G4 反例固化:blocking 非 bool → HIGH。"""
        vulns = validate_gate_config.validate_level("L1", {"blocking": "true"})
        assert "G4-BLOCKING-INVALID" in [v["code"] for v in vulns]

    def test_stage_empty(self, validate_gate_config):
        vulns = validate_gate_config.validate_level("L1", {"stage": ""})
        assert "G4-STAGE-EMPTY" in [v["code"] for v in vulns]

    def test_happy_valid_level_no_vulns(self, validate_gate_config):
        vulns = validate_gate_config.validate_level("L1", _valid_levels()["L1"])
        assert vulns == [], f"合法档位不应有 vuln, 得到 {vulns}"


# ============================================================================
# TestRunChecks — G5 缺档 + 端到端
# ============================================================================
class TestRunChecks:
    def test_missing_levels_key(self, validate_gate_config, tmp_path):
        p = _write_config(tmp_path, {"version": "1.0.0"})
        vulns, _ = validate_gate_config.run_checks(p)
        assert "G1-GATE-CONFIG-MISSING-LEVELS" in [v["code"] for v in vulns]

    def test_missing_level_gives_warning(self, validate_gate_config, tmp_path):
        """G5:缺 L4 档 → WARN 不阻断。"""
        levels = _valid_levels()
        levels.pop("L4")
        p = _write_config(tmp_path, {"levels": levels})
        vulns, warnings = validate_gate_config.run_checks(p)
        assert vulns == []
        assert any("L4" in w for w in warnings)

    def test_full_valid_config_no_errors(self, validate_gate_config, tmp_path):
        p = _write_config(tmp_path, {"levels": _valid_levels()})
        vulns, warnings = validate_gate_config.run_checks(p)
        assert vulns == []
        assert warnings == []


# ============================================================================
# TestRealGateConfig — 内置 scaffold 必须通过
# ============================================================================
class TestRealGateConfig:
    def test_real_config_passes(self, validate_gate_config, real_gate_config_path):
        """内置 nodejs scaffold 的 gate-config.json 必须 schema 合法。"""
        assert real_gate_config_path.exists(), "内置 gate-config.json 必须存在"
        vulns, warnings = validate_gate_config.run_checks(real_gate_config_path)
        assert vulns == [], f"内置 gate-config.json 不应有 vuln, 得到 {vulns}"


# ============================================================================
# TestMain — CLI exit code
# ============================================================================
class TestMain:
    def test_missing_config_args(self, validate_gate_config, invoke_cli, tmp_path):
        rc, _, _ = invoke_cli(
            "validate-gate-config.py",
            ["--config", str(tmp_path / "nonexistent-zzz.json")],
        )
        assert rc == validate_gate_config.EXIT_VULN
        assert validate_gate_config.EXIT_VULN == 1

    def test_happy_path_exit_0(self, invoke_cli, tmp_path):
        """PASS 态:合法 config → exit 0。"""
        p = _write_config(tmp_path, {"levels": _valid_levels()})
        rc, _, _ = invoke_cli("validate-gate-config.py", ["--config", str(p)])
        assert rc == 0

    @pytest.mark.trap
    def test_vuln_path_exit_nonzero(self, invoke_cli, tmp_path):
        """反例固化:非法 config → exit != 0。"""
        p = _write_config(tmp_path, {"levels": {"L1": {"checks": 123}}})
        rc, stdout, _ = invoke_cli("validate-gate-config.py", ["--config", str(p)])
        assert rc == 1
        assert "G2-LEVEL-MISSING-FIELD" in stdout or "G3-CHECKS-NOT-LIST" in stdout