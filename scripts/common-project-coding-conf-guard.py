#!/usr/bin/env python3
"""
scripts/common-project-coding-conf-guard.py — cpcc 项目侧薄壳守卫 (2026-08-21 guard-smith 委派落地)

设计目的:
  common-project-coding-conf(cpcc) 是通用项目级编码配置中心,含:
    - 路由表 (§1,场景→必加载 skills)
    - 自检机制 (§2,cpcc-self-check.mjs 6 项检查)
    - forge 协议 (§3,把 .trae/rules/*.md 锻造为 .trae/skills/project_rules_skills/)

  本守卫是项目侧薄壳入口 — 委托 skill 内置 cpcc-self-check.mjs 跑 6 项健康检查。
  遵循 AGENTS.md §1.11 铁律 11 — 项目侧 guard 必带,但实现可委托 skill 子目录脚本。

用法:
  python scripts/common-project-coding-conf-guard.py common-project-coding-conf
  python scripts/common-project-coding-conf-guard.py --node-check

退出码:
  0 = PASS (cpcc-self-check.mjs PASS)
  1 = BLOCK (cpcc-self-check.mjs FAIL / node 命令缺失 / 脚本缺失)
  2 = WARN  (留作未来扩展)

禁止:
  - 不要硬编码任何 key / token
  - 不要静默跳过任一检查
"""
# scan-whitelist-start
import subprocess  # noqa: F401
# scan-whitelist-end
import sys
import pathlib

# 项目根 = 本文件上一级
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_CPCC_SKILL_DIR = _REPO_ROOT / "skill-markets" / "common-project-coding-conf"
_CPCC_SELF_CHECK = _CPCC_SKILL_DIR / "scripts" / "cpcc-self-check.mjs"


def _check_skill_md() -> tuple:
    """检查 cpcc SKILL.md 存在 + frontmatter 完整。"""
    skill_md = _CPCC_SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        return False, f"cpcc SKILL.md 不存在: {skill_md}"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"cpcc SKILL.md 不可读: {e}"
    if not text.startswith("---"):
        return False, "cpcc SKILL.md 缺 YAML frontmatter"
    end = text.find("\n---", 3)
    if end < 0:
        return False, "cpcc SKILL.md frontmatter 未闭合"
    block = text[3:end]
    required = ("name:", "description:", "version:", "triggers:")
    missing = [k for k in required if k not in block]
    if missing:
        return False, f"cpcc SKILL.md frontmatter 缺字段: {', '.join(missing)}"
    return True, f"cpcc SKILL.md frontmatter OK ({skill_md.stat().st_size} bytes)"


def _check_self_check_script() -> tuple:
    """检查 cpcc-self-check.mjs 存在 + Node 语法 OK。"""
    if not _CPCC_SELF_CHECK.exists():
        return False, f"cpcc-self-check.mjs 不存在: {_CPCC_SELF_CHECK}"
    try:
        text = _CPCC_SELF_CHECK.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"cpcc-self-check.mjs 不可读: {e}"
    try:
        r = subprocess.run(
            ["node", "--check", str(_CPCC_SELF_CHECK)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(_REPO_ROOT),
            timeout=15,
        )
        if r.returncode != 0:
            return False, f"node --check cpcc-self-check.mjs 失败: {(r.stderr or r.stdout).strip()}"
    except FileNotFoundError:
        return False, "node 命令未找到"
    except subprocess.TimeoutExpired:
        return False, "node --check cpcc-self-check.mjs 超时(>15s)"
    return True, f"cpcc-self-check.mjs 语法 OK ({_CPCC_SELF_CHECK.stat().st_size} bytes)"


def _check_no_hardcoded_keys() -> tuple:
    """硬编码密钥扫描 — SKILL.md 全文扫描常见前缀(cpcc 是文档型 skill,scripts/.mjs 委托,本身不应含密钥)。"""
    import re
    patterns = (
        (r'(?i)(?:sk-[a-zA-Z0-9]{20,}|sk_live_|sk_test_)', 'AIGC-KEY-PREFIX'),
        (r'(?i)(?:AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16})', 'AWS-KEY-PREFIX'),
        (r'(?i)Bearer\s+[A-Za-z0-9\-_.]{20,}', 'BEARER-TOKEN'),
    )
    targets = [_CPCC_SKILL_DIR / "SKILL.md"]
    refs = _CPCC_SKILL_DIR / "references"
    if refs.exists():
        targets.extend(sorted(refs.rglob("*.md")))
    findings = 0
    for f in targets:
        if not f.exists() or not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pattern, tag in patterns:
            for m in re.finditer(pattern, text):
                snippet = m.group(0)
                if any(p in snippet.lower() for p in ('<your', 'xxx', 'placeholder', 'example', '${', '$env', 'os.environ')):
                    continue
                return False, f"[{tag}] 硬编码疑似密钥: {f.relative_to(_CPCC_SKILL_DIR)} → {snippet[:30]}..."
                findings += 1
    return True, ("硬编码密钥扫描通过" if findings == 0 else f"发现 {findings} 处疑似密钥")


def check_common_project_coding_conf(skill_path: str) -> dict:
    """cpcc 专属守卫 — 组合 3 项检查(SKILL.md / self-check.mjs / 密钥扫描)。"""
    errors: list = []
    warnings: list = []
    info: list = []

    if not _CPCC_SKILL_DIR.exists():
        errors.append(f"cpcc 技能目录不存在: {skill_path}")
        return {"passed": False, "errors": errors, "warnings": warnings, "info": info}

    checks = (
        ("cpcc SKILL.md frontmatter", _check_skill_md),
        ("cpcc-self-check.mjs 语法", _check_self_check_script),
        ("硬编码密钥扫描", _check_no_hardcoded_keys),
    )
    for label, fn in checks:
        ok, detail = fn()
        if not ok:
            errors.append(f"[{label}] {detail}")
        else:
            info.append(f"[{label}] {detail}")

    passed = len(errors) == 0
    return {"passed": passed, "errors": errors, "warnings": warnings, "info": info}


def main() -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(
        description="cpcc 项目侧薄壳守卫 (guard-smith 委派落地)",
        allow_abbrev=False,
    )
    parser.add_argument(
        "skill_path",
        nargs="?",
        default=str(_CPCC_SKILL_DIR),
        help="被 guard-router.mjs 传入的 positional argv(本守卫忽略)",
    )
    args = parser.parse_args()

    result = check_common_project_coding_conf(args.skill_path)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    info = result.get("info") or []
    warnings = result.get("warnings") or []
    errors = result.get("errors") or []
    passed = bool(result.get("passed", False))

    if info:
        print("\nℹ️  提示(不阻断):")
        for item in info:
            print(f"  - {item}")
    if warnings:
        print("\n⚠️  警告:")
        for w in warnings:
            print(f"  - {w}")
    if not passed:
        print("\n❌ cpcc 守卫检查失败:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\n✅ cpcc 守卫 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())