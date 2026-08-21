"""
ai-testmate 反例测试(必填/推荐/反例各 1,V11 §3.1 + protocol §5.1)
"""

import pathlib
import sys
import subprocess
import re
import json

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
GUARD_SCRIPT = SKILL_DIR / "scripts" / "ai-testmate-guard.py"
PROTOCOL_SCRIPT = SKILL_DIR / "scripts" / "publish-protocol.py"


def test_required_protocol_coverage_passes():
    """必填:协议覆盖自检必须 PASS(protocol §5.1 必填)"""
    r = subprocess.run(
        [sys.executable, str(PROTOCOL_SCRIPT)],
        capture_output=True, text=True, cwd=SKILL_DIR,
    )
    assert r.returncode == 0, f"publish-protocol.py 失败: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_zentao_write_authority_converged_to_reporter():
    """推荐:禅道写权仅收敛在 reporter.md(AP-3)"""
    agents = SKILL_DIR / "agents"
    pattern = re.compile(r"zentao (bug|testtask) create")
    violators = []
    for md in agents.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        if pattern.search(text) and md.name != "reporter.md":
            violators.append(md.name)
    assert violators == [], f"AP-3 越界: {violators} 含 zentao 写命令"


def test_lark_webhook_must_use_mcp_not_direct_url():
    """反例:禁止飞书直连 webhook URL(AP-4)"""
    pattern = re.compile(r"hooks\.lark|open\.feishu\.cn/open-apis/bot/v2/hook")
    violators = []
    for f in (SKILL_DIR / "scripts").rglob("*.sh"):
        text = f.read_text(encoding="utf-8")
        if pattern.search(text):
            violators.append(str(f.relative_to(SKILL_DIR)))
    # .env.example 也不允许
    env_ex = SKILL_DIR / ".env.example"
    if env_ex.exists() and pattern.search(env_ex.read_text(encoding="utf-8")):
        violators.append(".env.example")
    assert violators == [], f"AP-4 命中: {violators}"


def test_screenshot_redaction_in_ui_tester():
    """推荐:ui-tester.md 必带 mask/redact/脱敏(AP-5)"""
    ui = SKILL_DIR / "agents" / "ui-tester.md"
    text = ui.read_text(encoding="utf-8")
    assert re.search(r"mask|redact|脱敏", text), "AP-5:ui-tester.md 缺脱敏关键字"


def test_skill_md_under_350_lines():
    """推荐:SKILL.md ≤ 350 行(vibe-coding-standards v2.5 弹性)"""
    skill = SKILL_DIR / "SKILL.md"
    lines = len(skill.read_text(encoding="utf-8").splitlines())
    assert lines <= 350, f"SKILL.md {lines} 行 > 350"


def test_no_workspace_path_hardcoding_in_scripts():
    """推荐:scripts/ 无工作空间硬编码(AP-1)"""
    pattern = re.compile(r"/workspace/|/Users/[^/]+/|C:/workspace|C:\\\\workspace")
    for sh in (SKILL_DIR / "scripts").glob("*.sh"):
        text = sh.read_text(encoding="utf-8")
        assert not pattern.search(text), f"AP-1:{sh.name} 含工作空间硬编码"


def test_run_test_sh_has_timestamp():
    """推荐:run-test.sh 含时间戳(AP-7)"""
    rt = SKILL_DIR / "scripts" / "run-test.sh"
    text = rt.read_text(encoding="utf-8")
    assert re.search(r"YYYYMMDD|%Y%m%d|%y%m%d", text), "AP-7:run-test.sh 缺时间戳"


def test_no_python_path_hardcoding_in_scripts():
    """推荐:scripts/ 无 Python 路径硬编码(AP-6)"""
    pattern = re.compile(r"/mnt/c/|/usr/bin/python|/ProgramData/")
    for sh in (SKILL_DIR / "scripts").glob("*.sh"):
        text = sh.read_text(encoding="utf-8")
        # 允许 detect-python.sh 内部探测
        if sh.name == "detect-python.sh":
            continue
        assert not pattern.search(text), f"AP-6:{sh.name} 含 Python 路径硬编码"


# ===== v1.1 新增 6 用例(输入自适应 + 禅道降级) =====

def test_openapi_extractor_basic_conversion():
    """V2-AP-1:openapi 基本转换 + 鉴权字段不丢"""
    import yaml
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "demo"},
        "security": [{"bearerAuth": []}],
        "paths": {
            "/users/{id}": {
                "get": {
                    "operationId": "getUser",
                    "tags": ["core"],
                    "parameters": [{"name": "id", "in": "path", "required": True}],
                    "responses": {"200": {}, "404": {}},
                }
            }
        }
    }
    spec_file = SKILL_DIR / "tests" / "unit" / "_tmp_openapi.json"
    spec_file.write_text(json.dumps(spec), encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "openapi-extractor.py"),
             "--input", str(spec_file), "--mode", "auto"],
            capture_output=True, text=True, cwd=SKILL_DIR,
        )
        assert r.returncode == 0, f"openapi-extractor 失败:{r.stderr}"
        data = yaml.safe_load(r.stdout)
        assert len(data["test_cases"]) == 1
        c = data["test_cases"][0]
        assert c["data"]["auth_required"] is True, "V2-AP-1:鉴权字段丢失"
        assert c["data"]["path_params"]["id"] == "<fill>"
        assert c["data"]["expected_status"] == 200
        assert c["priority"] == "P0", f"core tag 应映射 P0,实际 {c['priority']}"
        assert c["source"] == "openapi"
    finally:
        spec_file.unlink(missing_ok=True)


def test_openapi_extractor_generates_negative_case():
    """V2-AP-1 变体:每 op 必生成至少 1 负例"""
    import yaml
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/items/{id}": {
                "get": {
                    "operationId": "getItem",
                    "responses": {"200": {}, "404": {}},
                }
            }
        }
    }
    spec_file = SKILL_DIR / "tests" / "unit" / "_tmp_openapi2.json"
    spec_file.write_text(json.dumps(spec), encoding="utf-8")
    try:
        r = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "openapi-extractor.py"),
             "--input", str(spec_file)],
            capture_output=True, text=True, cwd=SKILL_DIR,
        )
        data = yaml.safe_load(r.stdout)
        c = data["test_cases"][0]
        assert c["data"]["negative_cases"] is not None, "V2-AP-1:缺负例"
        assert c["data"]["negative_cases"][0]["expected_status"] == 404
        assert len(c["steps"]) >= 2, "V2-AP-1:steps 至少含正+负"
    finally:
        spec_file.unlink(missing_ok=True)


def test_planner_input_router_decision_matrix():
    """V2-AP-4:planner §1 决策矩阵 4 模式齐全(文档自检)"""
    router = SKILL_DIR / "references" / "input-router.md"
    text = router.read_text(encoding="utf-8")
    # 必须覆盖 4 模式标签
    assert "prd-only" in text
    assert "prd-tree" in text
    assert "prd+openapi" in text
    assert "openapi-only" in text
    # 用例 source 标签约定 4 个值(在反例段里出现)
    for s in ("prd", "prd-tree", "openapi", "mixed"):
        assert s in text, f"input-router.md 缺 source 值: {s}"


def test_planner_mode_d_no_prd_dependency():
    """V2-AP-5:planner §1 决策矩阵显式禁止模式 D 读 PRD"""
    planner = SKILL_DIR / "agents" / "planner.md"
    text = planner.read_text(encoding="utf-8")
    # 模式 D 必须有"跳过所有 PRD 操作"
    assert "模式 D" in text
    assert "跳过所有 PRD 操作" in text or "不读 PRD" in text


def test_reporter_zentao_optional_with_fallback():
    """V2-AP-2:reporter §3.3 含禅道降级到本地路径"""
    reporter = SKILL_DIR / "agents" / "reporter.md"
    text = reporter.read_text(encoding="utf-8")
    # 必须显式声明双路径
    assert "路径 A" in text and "路径 B" in text
    assert "本地 markdown" in text or "本地 bug" in text
    assert "降级" in text


def test_bug_storage_frontmatter_has_source_field():
    """V2-AP-3:bug 单 frontmatter 7 字段必带 source"""
    bug_md = SKILL_DIR / "references" / "bug-storage.md"
    text = bug_md.read_text(encoding="utf-8")
    # 必须出现 source 字段示例
    assert "source: qa-found" in text
    # 7 字段 ID/title/status/created/priority/severity/source
    required = ["id", "title", "status", "created", "priority", "severity", "source"]
    for f in required:
        assert f in text, f"bug-storage.md 缺字段 {f}"


# ===== v1.2 新增 3 用例(工作空间自动探测) =====

def test_workspace_detect_cwd_mode():
    """V3-2:cwd 直接含 .agents/.env → detected_mode=cwd"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
        (agents_dir / ".env").write_text("X=1\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "workspace-detect.py"),
             "--start", str(tmp_path), "--json"],
            capture_output=True, text=True,
        )
        assert r.returncode == 0, r.stderr
        import json
        data = json.loads(r.stdout)
        assert data["detected_mode"] == "cwd"
        assert data["workspace_root"] == str(tmp_path.resolve())
        assert data["env_file"].endswith(".env")


def test_workspace_detect_ancestor_mode():
    """V3-2 变体:从子目录向上找到 .agents/.env → detected_mode=ancestor"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = pathlib.Path(tmp)
        agents_dir = tmp_path / ".agents"
        agents_dir.mkdir()
        (agents_dir / ".env").write_text("X=1\n", encoding="utf-8")
        # 子目录,深度 2 层
        nested = tmp_path / "src" / "tests"
        nested.mkdir(parents=True)
        r = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "workspace-detect.py"),
             "--start", str(nested), "--json"],
            capture_output=True, text=True,
        )
        import json
        data = json.loads(r.stdout)
        assert data["detected_mode"] == "ancestor", f"应 ancestor,实际 {data['detected_mode']}"
        assert data["workspace_root"] == str(tmp_path.resolve())


def test_workspace_detect_strict_fallback_exit_2():
    """V3-2 变体:找不到 .agents/.env + --strict → exit 2"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        # tmp 目录无 .agents
        r = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts" / "workspace-detect.py"),
             "--start", tmp, "--strict"],
            capture_output=True, text=True,
        )
        assert r.returncode == 2, f"应 exit 2,实际 {r.returncode}"
        assert "未找到 .agents/.env" in r.stderr