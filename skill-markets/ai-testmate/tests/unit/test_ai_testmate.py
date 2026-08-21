"""
ai-testmate 反例测试(必填/推荐/反例各 1,V11 §3.1 + protocol §5.1)
"""

import pathlib
import sys
import subprocess
import re

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