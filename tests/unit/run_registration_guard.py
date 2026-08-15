#!/usr/bin/env python3
"""
Unit tests for skill-registration-guard.mjs (Guard Layer, 2026-08-14 §3 新增)

覆盖三态：
  - PASS : 真实注册表 + 真实 skill 目录 → 期望 exit 0
  - BLOCK : 真反例（缺注册 / 缺 guards / 幻影 skill / maintainer 不当）→ 期望 exit 1
  - 边界 : 极小化注册表 + 真 skill → 验证 schema 校验正确性

运行: python tests/unit/run_registration_guard.py
"""

import os
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

# Windows 默认 cp1252 控制台无法编码 ━━━ 等 Unicode 字符,
# 强制 stdout/stderr 用 utf-8
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GUARD = REPO_ROOT / "src" / "guards" / "skill-registration-guard.mjs"
REGISTRY_PATH = REPO_ROOT / "registry" / "skills.yaml"
NODE_BIN = os.environ.get("MY_TRAE_HELPER_NODE", "node")

passed = 0
failed = 0


def run_guard_in_tmp(tmp, args=None):
    """在临时仓库下运行守卫,通过 REG_GUARD_REPO_ROOT 环境变量覆盖路径"""
    cmd = [NODE_BIN, str(GUARD)]
    if args:
        cmd.extend(args)
    env = os.environ.copy()
    env["REG_GUARD_REPO_ROOT"] = str(tmp)
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    proc = subprocess.run(
        cmd, capture_output=True, text=True,
        env=env, cwd=str(tmp),
        creationflags=creationflags
    )
    return proc.returncode, proc.stdout, proc.stderr


def run_guard(args=None):
    """在真实仓库下运行守卫"""
    cmd = [NODE_BIN, str(GUARD)]
    if args:
        cmd.extend(args)
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    proc = subprocess.run(
        cmd, capture_output=True, text=True,
        env=os.environ.copy(), cwd=str(REPO_ROOT),
        creationflags=creationflags
    )
    return proc.returncode, proc.stdout, proc.stderr


def make_tmp_repo():
    """创建临时仓库副本(完整 mirror + node_modules symlink)"""
    tmp = Path(tempfile.mkdtemp(prefix="reg-guard-test-"))

    # 复制 skill-markets 顶层结构(只复制 SKILL.md / AGENTS.md 文件,够守卫判定)
    src_sm = REPO_ROOT / "skill-markets"
    dst_sm = tmp / "skill-markets"
    dst_sm.mkdir()
    for entry in src_sm.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in ("docs", "my-deep-research", "skill-scaffold"):
            continue
        if not (entry / "SKILL.md").exists() and not (entry / "AGENTS.md").exists():
            continue
        dst = dst_sm / entry.name
        dst.mkdir()
        for f in ("SKILL.md", "AGENTS.md"):
            src_f = entry / f
            if src_f.exists():
                shutil.copy2(src_f, dst / f)

    # 创建空 registry/skills.yaml(测试会覆盖写入)
    (tmp / "registry").mkdir()
    (tmp / "registry" / "skills.yaml").write_text("", encoding="utf-8")

    # 复制 scripts/guards 目录(供守卫脚本 hook 引用 + 兼容 mode)
    src_scripts = REPO_ROOT / "scripts"
    dst_scripts = tmp / "scripts"
    dst_scripts.mkdir()
    for f in ("skill-structure-guard.py", "skill-security-guard.py",
              "skill-capability-guard.py", "guard-router.mjs"):
        src_f = src_scripts / f
        if src_f.exists():
            shutil.copy2(src_f, dst_scripts / f)

    # 复制 .husky (供 gates[].hooks 引用)
    src_husky = REPO_ROOT / ".husky"
    if src_husky.exists():
        shutil.copytree(src_husky, tmp / ".husky")

    # symlink node_modules 让守卫 import yaml 能工作
    src_nm = REPO_ROOT / "node_modules"
    dst_nm = tmp / "node_modules"
    if src_nm.exists():
        try:
            os.symlink(str(src_nm), str(dst_nm), target_is_directory=True)
        except OSError:
            # Windows 没开发者模式就 fallback — 改为 junction
            subprocess.run(["cmd", "/c", "mklink", "/J", str(dst_nm), str(src_nm)],
                           capture_output=True)

    # 也需要在 tmp 里建 src/guards 占位(否则守卫子脚本被 .mjs 的 import.meta 反推会失败)
    # 实际上守卫用 REG_GUARD_REPO_ROOT 覆盖了,只需要自己能找到自己就行
    # import.meta.url 永远是源文件绝对路径,所以守卫本身在 src/guards/skill-registration-guard.mjs
    # 我们从 REPO_ROOT 复制一份过去
    src_guards_dir = REPO_ROOT / "src" / "guards"
    dst_guards_dir = tmp / "src" / "guards"
    dst_guards_dir.mkdir(parents=True)
    if src_guards_dir.exists():
        for f in src_guards_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, dst_guards_dir / f.name)

    return tmp


def cleanup_tmp_repo(tmp):
    """清理临时仓库"""
    if tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)


def write_registry(tmp, content):
    """覆盖临时仓库的 registry/skills.yaml"""
    (tmp / "registry" / "skills.yaml").write_text(content, encoding="utf-8")


# ─── 测试用例 ───────────────────────────────────────────

print("━━━ skill-registration-guard.mjs ━━━\n")


# 1. PASS: 真实仓库完整注册表 → 期望 exit 0
print("[T1] PASS — 真实仓库 + 真实注册表")
code, out, err = run_guard()
assert code == 0, f"期望 exit 0, 实际 {code}\nstdout: {out}\nstderr: {err}"
assert "✅ PASS" in out, f"输出缺 PASS 标志:\n{out}"
print(f"  ✅ exit={code}, 包含 PASS 标志")
passed += 1


# 2. PASS: 单 skill 名查询
print("\n[T2] PASS — 单 skill 查询 (guard-gate-smith 自注册)")
code, out, err = run_guard(["guard-gate-smith"])
assert code == 0, f"期望 exit 0, 实际 {code}\n{err}"
assert "[guard-gate-smith]" in out, f"输出缺 skill 名:\n{out}"
print(f"  ✅ exit={code}, 单 skill 查询正常")
passed += 1


# 3. BLOCK: skill 目录存在但注册表缺条目 → 期望 exit 1
print("\n[T3] BLOCK — 未注册 skill (skill-markets 存在但 registry 无条目)")
tmp = make_tmp_repo()
try:
    # agent-dev-control-kit 目录存在(被复制),但只注册 coding-xinfa
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: coding-xinfa
    status: active
    guards:
      - { id: coding-xinfa-structure, category: structure, script: scripts/skill-structure-guard.py, triggers: [pre-commit] }
    gates:
      - { id: coding-xinfa-pre-commit, level: L1, hooks: [.husky/pre-commit], runs_guards: [coding-xinfa-structure] }
    maintainer: guard-smith
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1 (BLOCK), 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "未在 registry/skills.yaml 注册" in out, f"输出缺未注册错误:\n{out}"
    assert "agent-dev-control-kit" in out, f"输出未点名:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK 'agent-dev-control-kit' 未注册")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 4. BLOCK: 注册了但 skill 目录不存在 (幻影 skill)
print("\n[T4] BLOCK — 幻影 skill (注册表条目指向不存在的目录)")
tmp = make_tmp_repo()
try:
    # phantom-skill 不存在,但我们注册了它
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: phantom-skill
    status: active
    guards:
      - { id: phantom-structure, category: structure, script: scripts/skill-structure-guard.py, triggers: [pre-commit] }
    gates:
      - { id: phantom-pre-commit, level: L1, hooks: [.husky/pre-commit], runs_guards: [phantom-structure] }
    maintainer: guard-smith
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1, 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "phantom-skill" in out and "不存在" in out, f"输出缺幻影错误:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK 幻影 skill")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 5. BLOCK: guards 数组为空
print("\n[T5] BLOCK — 缺 guards 注册")
tmp = make_tmp_repo()
try:
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: agent-dev-control-kit
    status: active
    guards: []
    gates:
      - { id: adk-pre-commit, level: L1, hooks: [.husky/pre-commit], runs_guards: [adk-structure] }
    maintainer: guard-smith
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1, 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "缺 guards" in out or "无防护" in out, f"输出缺 guards 缺失错误:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK 缺 guards")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 6. BLOCK: gates[].hooks 指向不存在的文件
print("\n[T6] BLOCK — gate hook 文件不存在")
tmp = make_tmp_repo()
try:
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: agent-dev-control-kit
    status: active
    guards:
      - { id: adk-structure, category: structure, script: scripts/skill-structure-guard.py, triggers: [pre-commit] }
    gates:
      - { id: adk-pre-commit, level: L1, hooks: [.husky/non-existent-hook], runs_guards: [adk-structure] }
    maintainer: guard-smith
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1, 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "non-existent-hook" in out and "不存在" in out, f"输出缺 hook 缺失错误:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK hook 文件不存在")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 7. BLOCK: maintainer 不是 guard-smith
print("\n[T7] BLOCK — maintainer 不在白名单")
tmp = make_tmp_repo()
try:
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: agent-dev-control-kit
    status: active
    guards:
      - { id: adk-structure, category: structure, script: scripts/skill-structure-guard.py, triggers: [pre-commit] }
    gates:
      - { id: adk-pre-commit, level: L1, hooks: [.husky/pre-commit], runs_guards: [adk-structure] }
    maintainer: rogue-agent
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1, 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "maintainer" in out and "白名单" in out, f"输出缺 maintainer 错误:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK maintainer 不当")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 8. BLOCK: status 不合法
print("\n[T8] BLOCK — status 字段不合法")
tmp = make_tmp_repo()
try:
    write_registry(tmp, """version: 1.0.0
description: 测试用极简注册表
skills:
  - skill: agent-dev-control-kit
    status: pending
    guards:
      - { id: adk-structure, category: structure, script: scripts/skill-structure-guard.py, triggers: [pre-commit] }
    gates:
      - { id: adk-pre-commit, level: L1, hooks: [.husky/pre-commit], runs_guards: [adk-structure] }
    maintainer: guard-smith
""")
    code, out, err = run_guard_in_tmp(tmp)
    assert code == 1, f"期望 exit 1, 实际 {code}\nstdout: {out}\nstderr: {err}"
    assert "status 不合法" in out, f"输出缺 status 错误:\n{out}"
    print(f"  ✅ exit={code}, 正确 BLOCK status 不合法")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# 9. 边界: 注册表文件不存在
print("\n[T9] 边界 — 注册表文件不存在")
tmp = make_tmp_repo()
try:
    (tmp / "registry" / "skills.yaml").unlink()
    code, out, err = run_guard_in_tmp(tmp)
    out_all = out + err
    assert code == 1, f"期望 exit 1, 实际 {code}\n{out_all}"
    assert "注册表不存在" in out_all, f"输出缺注册表缺失错误:\n{out_all}"
    print(f"  ✅ exit={code}, 正确 BLOCK 注册表文件缺失")
    passed += 1
finally:
    cleanup_tmp_repo(tmp)


# ─── 汇总 ───────────────────────────────────────────────
# V11.8.0 P0 修复(2026-08-15):pytest collect 时触发 sys.exit 导致全 INTERNALERROR
# 改成 __main__ 包裹:脚本式独立运行时仍按 0/1 退出,pytest 导入时不触发
if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"结果: ✅ {passed} 通过  ❌ {failed} 失败")
    print(f"{'='*50}")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)