"""
tests/unit/test_manifest_assert.py
按 agent-dev-control-kit §11.1.3 强制铁律:反例必须固化进 tests/unit/test_*.py

覆盖 4 态:
  - PASS: 全交付物齐全
  - BLOCK-缺脚本: 删 scripts/ 下的声明文件 → exit 2 + AGENT-PROMPT
  - BLOCK-缺文档: README/SKILL.md 缺必含章节 → exit 2 + AGENT-PROMPT
  - WARN: 改未声明文件 → exit 0(只警告)
  - EMPTY: 无意图 → exit 0

所有反例都用 tmp 目录隔离,不污染真实仓库。
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]  # d:\workspace\my-trae-helper
MANIFEST_SRC = ROOT / "skill-markets" / "MANIFEST.yaml"


# ---------- helper ----------
def run_manifest_assert(manifest_path: Path, intents: dict, repo_root: Path) -> subprocess.CompletedProcess:
    """在指定 repo_root 下跑 manifest-assert.py,传 JSON intents"""
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "manifest-assert.py"),
        "--manifest", str(manifest_path),
        "--intents", json.dumps({"intents": intents}),
    ]
    return subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)


def write_manifest(p: Path, content: str):
    p.write_text(content, encoding="utf8")


# ---------- 测试用例 ----------
def test_pass_state_real_repo(tmp_path):
    """
    PASS 态:用仓库真实 trae-security-review 样本,本次 commit 仅改 SKILL.md
    → exit 0
    """
    if not MANIFEST_SRC.exists():
        pytest.skip("真实 Manifest 尚未生成")
    # 把真实 Manifest 复制到 tmp
    test_manifest = tmp_path / "MANIFEST.yaml"
    test_manifest.write_text(MANIFEST_SRC.read_text(encoding="utf8"), encoding="utf8")
    # 在 tmp 仓库里建一个 fake skill,文件结构与 Manifest 一致
    fake_skill = tmp_path / "skill-markets" / "trae-security-review"
    (fake_skill / "scripts").mkdir(parents=True)
    (fake_skill / "scripts" / "scan_skills_dir.py").write_text(
        "#!/usr/bin/env python3\n# CLI: scan\nif __name__ == '__main__':\n    import sys; sys.exit(0)\n", encoding="utf8"
    )
    (fake_skill / "scripts" / "rigor_scanner.py").write_text(
        "#!/usr/bin/env python3\n# CLI: scan\nif __name__ == '__main__':\n    import sys; sys.exit(0)\n", encoding="utf8"
    )
    (fake_skill / "scripts" / "scan_rigor.py").write_text(
        "#!/usr/bin/env python3\n# CLI: scan_rigor\nif __name__ == '__main__':\n    import sys; sys.exit(0)\n", encoding="utf8"
    )
    (fake_skill / "references").mkdir(parents=True, exist_ok=True)
    (fake_skill / "references" / "checklists.md").write_text("# checklists", encoding="utf8")
    (fake_skill / "SKILL.md").write_text("# trae-security-review\n\n## 架构概览\nxxx\n", encoding="utf8")
    # 测试文件
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / "tests" / "unit" / "test_security_guard.py").write_text(
        "# test\ndef test_real_skill_passes():\n    pass\n# skill-security-guard.py\n", encoding="utf8"
    )

    intents = [
        {"kind": "add-skill", "skill": "trae-security-review",
         "target": "trae-security-review", "path": "skill-markets/trae-security-review/SKILL.md"},
    ]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 0, f"应为 PASS,实际:\nstdout={r.stdout}\nstderr={r.stderr}"
    assert "PASS" in r.stdout


def test_block_missing_script(tmp_path):
    """
    BLOCK 态 - 缺脚本:Manifest 声明 scripts/foo.py 但实际不存在
    → exit 2 + AGENT-PROMPT 块
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, f"""
schema_version: 1
skills:
  - name: fake-skill
    scripts:
      - path: scripts/missing.py
        cli_entry: missing
        exit_codes: [0]
    docs: []
    tests: []
""")
    (tmp_path / "skill-markets" / "fake-skill").mkdir(parents=True)

    intents = [{"kind": "add-skill", "skill": "fake-skill", "target": "fake-skill", "path": "skill-markets/fake-skill/SKILL.md"}]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 2, f"应为 BLOCK(2),实际={r.returncode}\nstdout={r.stdout}"
    assert "[AGENT-PROMPT]" in r.stdout
    assert "[/AGENT-PROMPT]" in r.stdout
    assert "scripts/missing.py" in r.stdout
    assert '"kind": "script"' in r.stdout


def test_block_missing_doc_section(tmp_path):
    """
    BLOCK 态 - 缺文档章节:SKILL.md 存在但缺 ## 返回值
    → exit 2 + AGENT-PROMPT 含 fix 指引
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, """
schema_version: 1
skills:
  - name: fake-skill
    scripts: []
    docs:
      - path: SKILL.md
        must_contain:
          - "## 用法"
          - "## 返回值"
    tests: []
""")
    skill = tmp_path / "skill-markets" / "fake-skill"
    skill.mkdir(parents=True)
    # SKILL.md 只有 ## 用法,缺 ## 返回值
    (skill / "SKILL.md").write_text("# fake\n\n## 用法\nxxx\n", encoding="utf8")

    intents = [{"kind": "add-skill", "skill": "fake-skill", "target": "fake-skill", "path": "skill-markets/fake-skill/SKILL.md"}]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 2
    assert "[AGENT-PROMPT]" in r.stdout
    assert "## 返回值" in r.stdout
    assert '"kind": "doc"' in r.stdout


def test_warn_unknown_skill(tmp_path):
    """
    WARN 态:本次涉及的 skill 不在 MANIFEST → exit 0 + [WARN] 行
    (允许增量添加,只警告不阻断)
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, """
schema_version: 1
skills: []
""")
    (tmp_path / "skill-markets" / "totally-new-skill").mkdir(parents=True)

    intents = [{"kind": "add-skill", "skill": "totally-new-skill", "target": "totally-new-skill", "path": "skill-markets/totally-new-skill/SKILL.md"}]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 0
    assert "[WARN]" in r.stdout


def test_empty_intents(tmp_path):
    """
    EMPTY 态:无 intents(本次变更不涉及 skill-markets/)→ exit 0 跳过
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, """
schema_version: 1
skills:
  - name: whatever
    scripts: []
    docs: []
    tests: []
""")
    r = run_manifest_assert(test_manifest, [], tmp_path)
    assert r.returncode == 0
    assert "跳过" in r.stdout


def test_block_missing_test_keyword(tmp_path):
    """
    BLOCK 态 - 缺测试断言关键词:测试文件存在但缺少必含关键词
    → exit 2
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, """
schema_version: 1
skills:
  - name: fake-skill
    scripts: []
    docs: []
    tests:
      - path: tests/unit/test_fake.py
        must_assert:
          - "MAGIC_KEYWORD"
""")
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / "tests" / "unit" / "test_fake.py").write_text("# only common stuff\n", encoding="utf8")

    intents = [{"kind": "add-skill", "skill": "fake-skill", "target": "fake-skill", "path": "skill-markets/fake-skill/SKILL.md"}]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 2
    assert "MAGIC_KEYWORD" in r.stdout
    assert '"kind": "test"' in r.stdout


def test_full_manifest_all_skills(tmp_path):
    """
    全量级测试:用真实生成的 Manifest,遍历所有 39 个 skill 同时做 add-skill,
    期望全部 PASS(只要仓库当前状态完整)
    """
    if not MANIFEST_SRC.exists():
        pytest.skip("Manifest 尚未生成")
    test_manifest = tmp_path / "MANIFEST.yaml"
    test_manifest.write_text(MANIFEST_SRC.read_text(encoding="utf8"), encoding="utf8")

    # 在 tmp 里复刻所有真实 skill 的最小骨架
    import yaml
    manifest_data = yaml.safe_load(test_manifest.read_text(encoding="utf8"))
    skills_spec = {s["name"]: s for s in manifest_data["skills"]}

    for skill_name, spec in skills_spec.items():
        skill_root = tmp_path / "skill-markets" / skill_name
        # scripts
        for sc in spec.get("scripts", []) or []:
            full = skill_root / sc["path"]
            full.parent.mkdir(parents=True, exist_ok=True)
            # 写一个最小可用的脚本(.py 走 __main__,.mjs 走 process.argv)
            if full.suffix == ".py":
                full.write_text("#!/usr/bin/env python3\nif __name__ == '__main__':\n    import sys; sys.exit(0)\n", encoding="utf8")
            elif full.suffix in (".mjs", ".js"):
                full.write_text("#!/usr/bin/env node\nprocess.argv;\n", encoding="utf8")
            elif full.suffix == ".sh":
                full.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf8")
        # docs
        for doc in spec.get("docs", []) or []:
            full = skill_root / doc["path"]
            full.parent.mkdir(parents=True, exist_ok=True)
            # 包含所有 must_contain 字符串
            content = f"# {skill_name}\n\n"
            for phrase in doc.get("must_contain", []) or []:
                content += f"{phrase}\n"
            full.write_text(content, encoding="utf8")

    # 构造全量 intents
    intents = [
        {"kind": "add-skill", "skill": s["name"], "target": s["name"],
         "path": f"skill-markets/{s['name']}/SKILL.md"}
        for s in manifest_data["skills"]
    ]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 0, f"全量 PASS 失败:\nstdout={r.stdout[:2000]}\nstderr={r.stderr}"
    assert "PASS" in r.stdout
    assert str(len(intents)) in r.stdout or "本次变更涉及的" in r.stdout


def test_block_python_script_no_cli(tmp_path):
    """
    BLOCK 态 - Python 脚本缺 CLI 入口
    → exit 2 + fix 指引提到 if __name__ == '__main__'
    """
    test_manifest = tmp_path / "MANIFEST.yaml"
    write_manifest(test_manifest, """
schema_version: 1
skills:
  - name: fake-skill
    scripts:
      - path: scripts/no_cli.py
        cli_entry: no_cli
        exit_codes: [0]
    docs: []
    tests: []
""")
    skill = tmp_path / "skill-markets" / "fake-skill"
    skill.mkdir(parents=True)
    (skill / "scripts").mkdir()
    # 只有 print,没有 __name__ 块
    (skill / "scripts" / "no_cli.py").write_text("print('hello')\n", encoding="utf8")

    intents = [{"kind": "add-script", "skill": "fake-skill", "target": "fake-skill/scripts/no_cli.py", "path": "skill-markets/fake-skill/scripts/no_cli.py"}]
    r = run_manifest_assert(test_manifest, intents, tmp_path)
    assert r.returncode == 2
    assert "__name__" in r.stdout or "argparse" in r.stdout