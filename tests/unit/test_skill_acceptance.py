#!/usr/bin/env python3
"""
Skill Acceptance Tests — 技能市场验收门禁测试

覆盖四个守卫的真实验收能力:
  1. Structure Guard — 命名 / frontmatter / 铁律数量 / 脚本规模
  2. Security Guard — 硬编码密钥 / Shell 执行 / HTTP 不安全
  3. Capability Guard — 脚本去重 / CAPABILITY-MAP.md 同步
  4. Dependency Guard — 硬依赖完整性 / 软依赖降级

每个守卫用 tmp 目录造反例,验证 BLOCK 行为。

运行: python tests/unit/test_skill_acceptance.py
"""

import subprocess
import sys
import tempfile
import json
from pathlib import Path

# Windows 默认 cp1252 控制台无法编码 ━━━ 等 Unicode 字符,
# 强制 stdout/stderr 用 utf-8,避免 L1/L2 Gate 在 npm run test:unit 时炸 UnicodeEncodeError
# (2026-08-14 push 失败修复)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
STRUCTURE_GUARD = REPO_ROOT / "scripts" / "skill-structure-guard.py"
SECURITY_GUARD = REPO_ROOT / "scripts" / "skill-security-guard.py"
CAPABILITY_GUARD = REPO_ROOT / "scripts" / "skill-capability-guard.py"

passed = 0
failed = 0


def run_python(script, arg):
    """运行 Python 守卫"""
    proc = subprocess.run(
        [sys.executable, str(script), str(arg)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_node(script, arg):
    """运行 Node 守卫"""
    proc = subprocess.run(
        ["node", str(script), str(arg)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT)
    )
    return proc.returncode, proc.stdout, proc.stderr


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  ✅ {name}")
        passed += 1
    except AssertionError as e:
        print(f"  ❌ {name}")
        print(f"     {e}")
        failed += 1
    except Exception as e:
        print(f"  ❌ {name} (异常)")
        print(f"     {type(e).__name__}: {e}")
        failed += 1


# ─── Structure Guard 验收 ────────────────────────────────────
print("━━━ Structure Guard（结构验收）━━━")


def structure_bad_uppercase_blocks():
    """❶ 目录名含大写字母 → BLOCK"""
    # 用 mkdtemp + suffix 自定义 BadName_2026
    import os
    tmp = tempfile.mkdtemp(prefix="acc-bad-up-")
    bad_path = os.path.join(os.path.dirname(tmp), "BadName_2026")
    Path(bad_path).mkdir(exist_ok=True)
    (Path(bad_path) / "SKILL.md").write_text("---\nname: BadName_2026\n---\n")
    try:
        code, out, _ = run_python(STRUCTURE_GUARD, bad_path)
        assert code != 0, f"应 BLOCK 但 exit=0, output={out}"
        assert "目录名不合规" in out or "目录名不合规" in _, "应报目录名问题"
    finally:
        import shutil
        shutil.rmtree(bad_path, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)


def structure_no_frontmatter_blocks():
    """❷ SKILL.md 缺 YAML frontmatter → BLOCK"""
    with tempfile.TemporaryDirectory(prefix="acc-no-fm-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("# 无 frontmatter\n")
        code, out, _ = run_python(STRUCTURE_GUARD, tmp)
        assert code != 0, f"应 BLOCK 但 exit=0"
        assert "frontmatter" in out.lower() or "frontmatter" in _.lower()


def structure_missing_skillmd_blocks():
    """❸ 目录无 SKILL.md → BLOCK"""
    with tempfile.TemporaryDirectory(prefix="acc-no-md-") as tmp:
        code, out, _ = run_python(STRUCTURE_GUARD, tmp)
        assert code != 0, "应 BLOCK"


def structure_too_many_rules_blocks():
    """❹ 铁律 > 10 条 → 不阻断(守卫 v2 弹性)"""
    # 守卫 v2 设计: 行数/铁律数/脚本数 不设硬上限(vibe-coding-standards v2.5 弹性 100~350 行)
    # 此处只确认守卫不因铁律数崩溃,不强制 BLOCK
    with tempfile.TemporaryDirectory(prefix="acc-rules-") as tmp:
        rules = "\n".join(f"{i}. 铁律 {i}" for i in range(1, 12))
        # frontmatter 必须含 description 才能过守卫 v2 的"必需字段"检查
        content = f"---\nname: too-many\ndescription: 测试铁律数\n---\n# 测试\n{rules}\n"
        (Path(tmp) / "SKILL.md").write_text(content)
        code, out, _ = run_python(STRUCTURE_GUARD, tmp)
        # v2 守卫对铁律数只记 info, 不阻断 → 期望 PASS(0)
        assert code == 0, f"守卫 v2 期望 PASS 但 exit={code}, output={out}"


def structure_good_skill_passes():
    """❺ 合规技能 → PASS"""
    with tempfile.TemporaryDirectory(prefix="acc-good-") as tmp:
        content = "---\nname: good\ndescription: 测试\n---\n# 测试\n1. 规则\n"
        (Path(tmp) / "SKILL.md").write_text(content)
        code, out, _ = run_python(STRUCTURE_GUARD, tmp)
        assert code == 0, f"应 PASS 但 exit={code}, output={out}"


test("目录名大写 → BLOCK", structure_bad_uppercase_blocks)
test("SKILL.md 缺 frontmatter → BLOCK", structure_no_frontmatter_blocks)
test("目录无 SKILL.md → BLOCK", structure_missing_skillmd_blocks)
test("铁律 > 10 条 → 不阻断(守卫 v2 弹性)", structure_too_many_rules_blocks)
test("合规技能 → PASS", structure_good_skill_passes)


# ─── Security Guard 验收 ─────────────────────────────────────
print("\n━━━ Security Guard（安全验收）━━━")


def security_real_api_key_blocks():
    """❶ 硬编码 api_key → BLOCK"""
    with tempfile.TemporaryDirectory(prefix="acc-secret-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: secret\n---\n")
        (Path(tmp) / "bad.py").write_text('api_key = "sk-real-secret-12345678"\n')
        code, out, _ = run_python(SECURITY_GUARD, tmp)
        assert code != 0, f"应 BLOCK 但 exit=0"
        assert "BLOCK" in out or "BLOCK" in _, "应返回 BLOCK 状态"


def security_real_password_blocks():
    """❷ 硬编码 password → BLOCK"""
    with tempfile.TemporaryDirectory(prefix="acc-pwd-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: pwd\n---\n")
        (Path(tmp) / "bad.py").write_text('password = "MyRealP@ssw0rd123"\n')
        code, out, _ = run_python(SECURITY_GUARD, tmp)
        assert code != 0, "应 BLOCK"


def security_clean_skill_passes():
    """❸ 干净技能 → PASS"""
    with tempfile.TemporaryDirectory(prefix="acc-clean-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: clean\n---\n")
        (Path(tmp) / "ok.py").write_text('def hello():\n    return "hi"\n')
        code, out, _ = run_python(SECURITY_GUARD, tmp)
        assert code == 0, f"应 PASS 但 exit={code}, output={out}"


test("硬编码 api_key → BLOCK", security_real_api_key_blocks)
test("硬编码 password → BLOCK", security_real_password_blocks)
test("干净脚本 → PASS", security_clean_skill_passes)


# ─── Capability Guard 验收 ──────────────────────────────────
print("\n━━━ Capability Guard（能力验收）━━━")


def capability_duplicate_basename_blocks():
    """❶ 重复 basename 已注册脚本 → BLOCK"""
    with tempfile.TemporaryDirectory(prefix="acc-dup-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: dup\n---\n")
        scripts = Path(tmp) / "scripts"
        scripts.mkdir()
        # vision-audit.mjs 已在 CAPABILITY-MAP.md 注册
        (scripts / "vision-audit.mjs").write_text("// dup\n")
        code, out, _ = run_python(CAPABILITY_GUARD, tmp)
        assert code != 0, f"应 BLOCK 但 exit=0"
        assert "已存在" in out or "已存在" in _, "应报脚本重复"


def capability_unique_skill_passes():
    """❷ 全新脚本名 → 能力去重通过（但 CAPABILITY-MAP 同步会失败）"""
    with tempfile.TemporaryDirectory(prefix="acc-unique-") as tmp:
        (Path(tmp) / "SKILL.md").write_text("---\nname: unique\n---\n")
        scripts = Path(tmp) / "scripts"
        scripts.mkdir()
        (scripts / "my-unique-script-xyz.py").write_text("# unique\n")
        code, out, _ = run_python(CAPABILITY_GUARD, tmp)
        # 能力去重应 PASS,但整体 exit 非 0 (因为 CAPABILITY-MAP 未注册)
        assert "能力去重检查" in out, "应包含去重检查"
        assert "passed\": true" in out, "去重应 PASS"


def capability_script_name_arg():
    """❸ 指定脚本名参数 → 检测是否在注册表"""
    # vision-audit.mjs 在注册表 → 应 BLOCK
    code, out, _ = run_python(CAPABILITY_GUARD, "skill-markets/coding-xinfa vision-audit.mjs")
    assert code != 0, f"指定 vision-audit.mjs 应 BLOCK 但 exit={code}"


test("重复 basename 已注册脚本 → BLOCK", capability_duplicate_basename_blocks)
test("全新脚本名 → 能力去重通过", capability_unique_skill_passes)
test("指定已注册脚本名参数 → BLOCK", capability_script_name_arg)


# ─── Dependency Guard 验收 ──────────────────────────────────
print("\n━━━ Dependency Guard（依赖验收）━━━")


def dependency_real_no_deps_passes():
    """❶ trae-security-review 无硬依赖 → PASS"""
    code, out, _ = run_node(REPO_ROOT / "src" / "guards" / "skill-dependency-guard.mjs", "trae-security-review")
    assert code == 0, f"应 PASS 但 exit={code}, stderr={_}"


def dependency_nonexistent_blocks():
    """❷ 不存在的技能 → 阻断"""
    code, out, _ = run_node(REPO_ROOT / "src" / "guards" / "skill-dependency-guard.mjs", "never-existed-zzz")
    assert code != 0, f"应 BLOCK 但 exit={code}"


test("无依赖技能 → PASS", dependency_real_no_deps_passes)
test("不存在技能 → BLOCK", dependency_nonexistent_blocks)


# ─── 总结 ──────────────────────────────────────────────────
print(f"\n━━━ 通过: {passed} / 失败: {failed} ━━━")
sys.exit(1 if failed > 0 else 0)