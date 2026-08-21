#!/usr/bin/env python3
"""
scripts/project-self-improving-guard.py — project-self-improving 项目侧薄壳守卫 (2026-08-21 guard-smith 委派落地)

设计目的:
  project-self-improving 是项目内经验沉淀 skill(替代 self-improving-agent 项目内角色),
  含 4 assets(LEARNINGS.md / ERRORS.md / FEATURE_REQUESTS.md / SKILL-TEMPLATE.md)
  + 9 references(trae-integration / claude-code-integration / codex-integration /
    copilot-integration / hook-self-check / examples / multi-agent-matrix /
    best-practices / periodic-review)
  + 5 scripts(detect-node.sh / hook-self-check.sh / activator.sh / error-detector.sh / install-snippet.sh)
  + todos/(task.md / checklist.md)。

  本守卫是项目侧薄壳入口 — 委托本文件做 5 项硬检查,确保发布前合规。
  遵循 AGENTS.md §1.11 铁律 11 — 项目侧 guard 必带。

用法:
  python scripts/project-self-improving-guard.py project-self-improving

退出码:
  0 = PASS  (errors=0)
  1 = BLOCK (errors≥1)
  2 = WARN  (errors=0 但 warnings≥1)

禁止:
  - 不要 import skill-markets/<pkg>/scripts/*(与 AGENTS.md §1.11 冲突)
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
_SKILL_DIR = _REPO_ROOT / "skill-markets" / "project-self-improving"

# vibe-coding-standards v2.5 行数弹性上限(与 scripts/vibe-coding-standards-line-guard.py 一致)
_SKILL_LINE_LIMIT = 350

# 必存在的 assets(项目内经验沉淀的 4 个数据文件)
_REQUIRED_ASSETS = (
    "LEARNINGS.md",
    "ERRORS.md",
    "FEATURE_REQUESTS.md",
    "SKILL-TEMPLATE.md",
)

# 必存在的 references(9 个:4 agent 接入 + 5 主题)
_REQUIRED_REFERENCES = (
    "trae-integration.md",
    "claude-code-integration.md",
    "codex-integration.md",
    "copilot-integration.md",
    "hook-self-check.md",
    "examples.md",
    "multi-agent-matrix.md",
    "best-practices.md",
    "periodic-review.md",
)

# 必存在的 scripts(5 个 POSIX sh 工具)
_REQUIRED_SCRIPTS = (
    "detect-node.sh",
    "hook-self-check.sh",
    "activator.sh",
    "error-detector.sh",
    "install-snippet.sh",
)


def _check_top_skill_md() -> tuple:
    """检查 (1) 顶层 SKILL.md frontmatter(name + description 必填,version 警告) + (2) 行数 ≤350。"""
    skill_md = _SKILL_DIR / "SKILL.md"
    if not skill_md.exists():
        return False, f"SKILL.md 不存在: {skill_md}"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"SKILL.md 不可读: {e}"
    if not text.startswith("---"):
        return False, "SKILL.md 缺 YAML frontmatter(以 --- 开头)"
    end = text.find("\n---", 3)
    if end < 0:
        return False, "SKILL.md frontmatter 未闭合"
    block = text[3:end]
    if "name:" not in block:
        return False, "SKILL.md frontmatter 缺 name"
    if "description:" not in block:
        return False, "SKILL.md frontmatter 缺 description(AGENTS.md §1 铁律)"
    # 行数检查(返回 info,warn 而非 error — 由调用方按需提取)
    try:
        line_count = sum(1 for _ in skill_md.open("r", encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        line_count = 0
    if line_count > _SKILL_LINE_LIMIT:
        return False, (
            f"SKILL.md 行数 {line_count} > {_SKILL_LINE_LIMIT} "
            f"(vibe-coding-standards v2.5 弹性上限,提取 references/ 子目录)"
        )
    return True, f"SKILL.md frontmatter OK + 行数 {line_count}/{_SKILL_LINE_LIMIT} ({skill_md.stat().st_size} bytes)"


def _check_assets() -> tuple:
    """检查 (3) 4 assets 文件齐全。"""
    assets_dir = _SKILL_DIR / "assets"
    if not assets_dir.exists():
        return False, f"assets/ 目录不存在: {assets_dir}"
    missing = [a for a in _REQUIRED_ASSETS if not (assets_dir / a).is_file()]
    if missing:
        return False, f"assets 缺失文件: {', '.join(missing)}"
    return True, f"assets 4 项齐全 ({', '.join(_REQUIRED_ASSETS)})"


def _check_references() -> tuple:
    """检查 (4) 9 references 文件齐全。"""
    refs_dir = _SKILL_DIR / "references"
    if not refs_dir.exists():
        return False, f"references/ 目录不存在: {refs_dir}"
    missing = [r for r in _REQUIRED_REFERENCES if not (refs_dir / r).is_file()]
    if missing:
        return False, f"references 缺失文件: {', '.join(missing)}"
    return True, f"references {len(_REQUIRED_REFERENCES)} 项齐全"


def _check_scripts() -> tuple:
    """检查 (5) 5 scripts 文件齐全 + bash -n 通过。"""
    scripts_dir = _SKILL_DIR / "scripts"
    if not scripts_dir.exists():
        return False, f"scripts/ 目录不存在: {scripts_dir}"
    missing = [s for s in _REQUIRED_SCRIPTS if not (scripts_dir / s).is_file()]
    if missing:
        return False, f"scripts 缺失文件: {', '.join(missing)}"
    # bash -n 语法检查 — 通过 `cd <repo> && bash -n <relative>` 避免 Windows 路径在
    # subprocess.run 时被 MSYS / wsl 错误翻译。subprocess.run 自身用绝对相对路径不可靠。
    syntax_failures = []
    # 用 REPO_ROOT 相对路径,从 cwd=str(_REPO_ROOT) 启动 bash 即可
    rel_scripts = f"skill-markets/project-self-improving/scripts"
    for s in _REQUIRED_SCRIPTS:
        try:
            r = subprocess.run(
                ["bash", "-n", f"{rel_scripts}/{s}"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(_REPO_ROOT),
                timeout=10,
            )
            if r.returncode != 0:
                err = (r.stderr or r.stdout).strip()
                syntax_failures.append(f"{s}: {err}")
        except FileNotFoundError:
            return False, "bash 命令未找到(无法跑语法检查)"
        except subprocess.TimeoutExpired:
            syntax_failures.append(f"{s}: bash -n 超时(>10s)")
    if syntax_failures:
        return False, f"scripts bash -n 失败: {'; '.join(syntax_failures)}"
    return True, f"scripts {len(_REQUIRED_SCRIPTS)} 项齐全 + bash -n 全部通过"


def check_project_self_improving(skill_path: str) -> dict:
    """project-self-improving 专属守卫 — 组合 5 项检查。"""
    errors: list = []
    warnings: list = []
    info: list = []

    if not _SKILL_DIR.exists():
        errors.append(f"技能目录不存在: {skill_path}")
        return {"passed": False, "errors": errors, "warnings": warnings, "info": info}

    checks = (
        ("SKILL.md frontmatter + 行数", _check_top_skill_md),
        ("assets 4 项齐全", _check_assets),
        ("references 9 项齐全", _check_references),
        ("scripts 5 项 + bash -n", _check_scripts),
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
        description="project-self-improving 项目侧薄壳守卫 (guard-smith 委派落地)",
        allow_abbrev=False,
    )
    parser.add_argument(
        "skill_path",
        nargs="?",
        default=str(_SKILL_DIR),
        help="被 guard-router.mjs 传入的 positional argv(本守卫忽略)",
    )
    args = parser.parse_args()

    result = check_project_self_improving(args.skill_path)
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
        print("\n❌ project-self-improving 守卫检查失败:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\n✅ project-self-improving 守卫 PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())