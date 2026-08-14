"""validate-gate-integrity 反例单元测试

每个用例对应 references/traps.md §AP-* 反例 + Gate 自验收铁律 §11.1.x。

覆盖维度:
  - V1 必填脚本缺失
  - V2 echo-skip 占位脚本
  - V3 husky fake-skip body
  - V4 工具未安装
  - YAML / YAML 缺失双路径
  - scaffold_id 自动检测
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


# ============================================================================
# Helper — 构造符合 scaffold.yaml 要求的目标项目
# ============================================================================
@pytest.fixture
def scaffold_dir(validate_gate_integrity, skill_root):
    """返回 nodejs scaffold dir,供 validate-gate-integrity.find_scaffold_dir 用。"""
    sd = validate_gate_integrity.find_scaffold_dir("nodejs", skill_root)
    assert sd is not None, "内置 nodejs scaffold 必须存在"
    return sd


@pytest.fixture
def scaffold_required(validate_gate_integrity, scaffold_dir):
    """读取 scaffold.yaml 的 required_scripts 字段(真实数据)。"""
    cfg = validate_gate_integrity.parse_scaffold_yaml(scaffold_dir / "scaffold.yaml")
    return cfg.get("required_scripts") or {}


# ============================================================================
# TestIsEchoSkip — V2 反例 AP-2 Gate 静默跳过
# ============================================================================
class TestIsEchoSkip:
    @pytest.mark.trap
    @pytest.mark.parametrize(
        "body",
        [
            'echo "skipping lint"',
            "echo skipping",
            'echo "no lint configured"',
            ":",
            "true",
        ],
    )
    def test_placeholder_bodies_detected(self, validate_gate_integrity, body):
        """AP-2:占位脚本必须被判定为 fake。"""
        assert validate_gate_integrity.is_echo_skip(body) is True

    @pytest.mark.parametrize(
        "body",
        [
            "ruff check .",
            "node --check src/index.mjs",
            "pytest -q",
        ],
    )
    def test_real_scripts_not_flagged(self, validate_gate_integrity, body):
        """正常脚本不应被误判。"""
        assert validate_gate_integrity.is_echo_skip(body) is False


# ============================================================================
# TestIsFakeGateScript — V3 husky hook fake body
# ============================================================================
class TestIsFakeGateScript:
    @pytest.mark.trap
    def test_real_hook_not_flagged(self, validate_gate_integrity):
        body = """#!/usr/bin/env bash
set -e
echo "1️⃣ Lint..."
npm run lint
echo "2️⃣ TypeCheck..."
npm run typecheck
"""
        assert validate_gate_integrity.is_fake_gate_script(body) == []

    @pytest.mark.trap
    def test_fake_hook_flagged(self, validate_gate_integrity):
        body = '#!/usr/bin/env bash\ncommand -v npm >/dev/null || echo "skipping"\n'
        hits = validate_gate_integrity.is_fake_gate_script(body)
        assert len(hits) >= 1


# ============================================================================
# TestParseScaffoldYaml — YAML 路径与 fallback 路径
# ============================================================================
class TestParseScaffoldYaml:
    def test_parses_nodejs_scaffold_yaml(self, validate_gate_integrity, scaffold_dir):
        cfg = validate_gate_integrity.parse_scaffold_yaml(scaffold_dir / "scaffold.yaml")
        assert isinstance(cfg, dict)
        req = cfg.get("required_scripts") or {}
        # 真实 scaffold 必须含 pre_commit + pre_push
        assert "pre_commit" in req
        assert "pre_push" in req
        # nodejs scaffold 应要求 lint + test:unit(L1)
        assert "lint" in req["pre_commit"]
        # pre_push 应要求 build
        assert "build" in req["pre_push"]

    def test_fallback_when_yaml_missing(self, validate_gate_integrity, tmp_path):
        """fallback 解析器对纯文本 required_scripts 也应给出结构。"""
        f = tmp_path / "scaffold.yaml"
        f.write_text(
            "required_scripts:\n  pre_commit:\n    - lint\n    - test\n  pre_push:\n    - build\n",
            encoding="utf-8",
        )
        cfg = validate_gate_integrity.parse_scaffold_yaml(f)
        assert "lint" in (cfg.get("required_scripts", {}) or {}).get("pre_commit", [])


# ============================================================================
# TestAutoDetectScaffold — 5 栈自动识别
# ============================================================================
class TestAutoDetectScaffold:
    def test_detects_nodejs(self, validate_gate_integrity, tmp_path):
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) == "nodejs"

    def test_detects_python_pyproject(self, validate_gate_integrity, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) == "python"

    def test_detects_python_requirements(self, validate_gate_integrity, tmp_path):
        (tmp_path / "requirements.txt").write_text("requests\n", encoding="utf-8")
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) == "python"

    def test_detects_go(self, validate_gate_integrity, tmp_path):
        (tmp_path / "go.mod").write_text("module x\n", encoding="utf-8")
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) == "go"

    def test_detects_java_maven(self, validate_gate_integrity, tmp_path):
        (tmp_path / "pom.xml").write_text("<project/>", encoding="utf-8")
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) == "java-maven"

    def test_unknown_returns_none(self, validate_gate_integrity, tmp_path):
        assert validate_gate_integrity.auto_detect_scaffold(tmp_path) is None


# ============================================================================
# TestCheckNodejs — V1 + V2 路径
# ============================================================================
class TestCheckNodejs:
    @pytest.mark.trap
    def test_v1_no_pkg_json(self, validate_gate_integrity, tmp_path):
        """AP-2 触发:无 package.json → HIGH VULN。"""
        vulns = validate_gate_integrity.check_nodejs(tmp_path, {})
        codes = [v["code"] for v in vulns]
        assert "V1-NODEJS-NO-PKG" in codes
        assert any(v["severity"] == "HIGH" for v in vulns)

    def test_v1_missing_script_high(self, validate_gate_integrity, tmp_path, scaffold_required):
        """缺少 scaffold 要求的脚本 → HIGH。"""
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": {}}, ensure_ascii=False), encoding="utf-8"
        )
        vulns = validate_gate_integrity.check_nodejs(tmp_path, scaffold_required)
        codes = [v["code"] for v in vulns]
        assert "V1-NODEJS-MISSING-SCRIPT" in codes

    @pytest.mark.trap
    def test_v2_echo_skip_script_blocked(self, validate_gate_integrity, tmp_path, scaffold_required):
        """AP-2 关键:echo-skip 占位 → HIGH 阻断。"""
        # 满足所有 required_scripts,但内容是 echo skipping
        scripts = {s: 'echo "skipping lint"' for s in scaffold_required.get("pre_commit", [])}
        for s in scaffold_required.get("pre_push", []):
            scripts[s] = "echo skipping"
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": scripts}, ensure_ascii=False), encoding="utf-8"
        )
        vulns = validate_gate_integrity.check_nodejs(tmp_path, scaffold_required)
        codes = [v["code"] for v in vulns]
        assert "V2-NODEJS-ECHO-SKIP" in codes

    def test_happy_path_no_vulns(self, validate_gate_integrity, tmp_path, scaffold_required):
        scripts = {}
        for s in scaffold_required.get("pre_commit", []):
            scripts[s] = f"echo 'run {s}'"
        for s in scaffold_required.get("pre_push", []):
            scripts[s] = f"echo 'run {s}'"
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": scripts}, ensure_ascii=False), encoding="utf-8"
        )
        vulns = validate_gate_integrity.check_nodejs(tmp_path, scaffold_required)
        assert vulns == [], f"happy-path 不应有 vuln, 得到 {vulns}"


# ============================================================================
# TestCheckPython — V1-PY + V4-PY-TOOL
# ============================================================================
class TestCheckPython:
    @pytest.mark.trap
    def test_v1_no_pyproject(self, validate_gate_integrity, tmp_path):
        vulns = validate_gate_integrity.check_python(tmp_path, {})
        codes = [v["code"] for v in vulns]
        assert "V1-PY-NO-PYPROJECT" in codes

    def test_v1_no_build_backend_warning(self, validate_gate_integrity, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
        vulns = validate_gate_integrity.check_python(tmp_path, {"build_backend": True})
        codes = [v["code"] for v in vulns]
        assert "V1-PY-NO-BUILD-BACKEND" in codes

    def test_v1_build_backend_ok(self, validate_gate_integrity, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            "[project]\n[build-system]\nbuild-backend='x'\n", encoding="utf-8"
        )
        vulns = validate_gate_integrity.check_python(tmp_path, {"build_backend": True})
        codes = [v["code"] for v in vulns]
        assert "V1-PY-NO-BUILD-BACKEND" not in codes

    @pytest.mark.trap
    @pytest.mark.parametrize(
        "tool",
        ["totally-nonexistent-tool-xyz-12345"],
    )
    def test_v4_tool_missing(self, validate_gate_integrity, tmp_path, tool):
        (tmp_path / "pyproject.toml").write_text(
            "[project]\n[build-system]\nbuild-backend='x'\n", encoding="utf-8"
        )
        vulns = validate_gate_integrity.check_python(tmp_path, {"pre_commit": [tool]})
        codes = [v["code"] for v in vulns]
        assert "V4-PY-TOOL-MISSING" in codes


# ============================================================================
# TestCheckGateScripts — .husky hook 假体检测
# ============================================================================
class TestCheckGateScripts:
    @pytest.mark.trap
    def test_husky_fake_pre_commit_blocked(self, validate_gate_integrity, write_husky_hook, tmp_path):
        """AP-2:.husky/pre-commit 用 echo skipping → HIGH V3 vuln。"""
        # 用能命中 GATE_FAKE_BODY_PATTERNS 的真实 pattern
        write_husky_hook(
            tmp_path,
            "pre-commit",
            '#!/usr/bin/env bash\ncommand -v eslint >/dev/null 2>&1 || echo "skipping lint"\n',
        )
        vulns = validate_gate_integrity.check_gate_scripts(tmp_path, scaffold_dir=None)
        assert any(v["code"] == "V3-HUSKY-FAKE-BODY" for v in vulns), (
            f"应命中 fake-skip,得到 {vulns}"
        )

    def test_husky_without_dir_is_noop(self, validate_gate_integrity, tmp_path):
        """没有 .husky/ → 返回空列表(不阻断)。"""
        vulns = validate_gate_integrity.check_gate_scripts(tmp_path, scaffold_dir=None)
        assert vulns == []


# ============================================================================
# TestRunChecks — 端到端(不知道 scaffold 时给 INFO)
# ============================================================================
class TestRunChecks:
    def test_unknown_scaffold_returns_info(self, validate_gate_integrity, tmp_path):
        vulns, _ = validate_gate_integrity.run_checks(tmp_path, scaffold_id=None)
        codes = [v["code"] for v in vulns]
        assert "V0-UNKNOWN-SCAFFOLD" in codes

    def test_explicit_scaffold_id_used(self, validate_gate_integrity, tmp_path):
        vulns, sd = validate_gate_integrity.run_checks(tmp_path, scaffold_id="nodejs")
        assert sd is not None
        assert any(v["code"].startswith("V1-") for v in vulns)


# ============================================================================
# TestMain — JSON 输出 / 退出码 / 参数校验
# ============================================================================
class TestMain:
    def test_unknown_dir_exit_args(self, validate_gate_integrity, invoke_cli, tmp_path):
        rc, _, stderr = invoke_cli(
            "validate-gate-integrity.py",
            ["--target", str(tmp_path / "nonexistent-zzz")],
        )
        assert rc == validate_gate_integrity.EXIT_ARGS
        assert "not found" in stderr.lower() or "not found" in stderr

    def test_happy_path_json_output_exit_0(self, validate_gate_integrity, invoke_cli, tmp_path, scaffold_required):
        # 构造一个干净 nodejs 项目
        scripts = {
            s: f"echo run {s}"
            for s in (
                scaffold_required.get("pre_commit", [])
                + scaffold_required.get("pre_push", [])
            )
        }
        (tmp_path / "package.json").write_text(
            json.dumps({"scripts": scripts}, ensure_ascii=False), encoding="utf-8"
        )
        rc, stdout, _ = invoke_cli(
            "validate-gate-integrity.py",
            ["--target", str(tmp_path), "--scaffold-id", "nodejs", "--json"],
        )
        assert rc == 0
        payload = json.loads(stdout)
        assert payload["count"] == 0

    @pytest.mark.trap
    def test_vuln_path_exit_nonzero_with_message(
        self, validate_gate_integrity, invoke_cli, tmp_path
    ):
        """AP-2 反例固化:违规必须 exit != 0。"""
        # 没 package.json → V1 HIGH
        rc, stdout, _ = invoke_cli(
            "validate-gate-integrity.py",
            ["--target", str(tmp_path), "--scaffold-id", "nodejs"],
        )
        assert rc == 1
        assert "V1-NODEJS-NO-PKG" in stdout
