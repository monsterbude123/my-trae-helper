#!/usr/bin/env python3
"""
scripts/doc-sync-guard.py — 技能文档同步门禁 (2026-08-15 NEW)

设计目的:
  每次 commit 检查:若改了某个 skill 的 "实质性内容",要保证
    (a) 该 skill 一级目录下"给人类看的说明性文档"
    (b) 项目侧 5 项说明文档
  同步更新,否则硬阻断 (exit 1)。

触发时机: pre-commit (作为 Step 7, 放在 manifest bridge 之后)
调用方式:
  python scripts/doc-sync-guard.py                    # 默认:读 git diff --cached
  python scripts/doc-sync-guard.py --self-test        # 自检(造临时仓库 + 跑反例)
  python scripts/doc-sync-guard.py --repo-root PATH   # 覆盖 REPO_ROOT(测试用)

退出码:
  0 = PASS (无触发 或 全部同步)
  1 = BLOCK (任一 PKG 缺同步)
  2 = WARN-only (预留,本次未启用)

禁止:
  - 不要碰 skill-markets/<pkg>/scripts/(*-guard.py 必须项目侧)
  - 不要硬编码任何 key / token / 个人路径
  - 不要静默降级:任一 PKG 缺同步 = exit 1,绝不 "WARN 跳过"
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Callable, Dict, List, Set, Tuple

# Windows cp1252 兜底(AGENTS.md §4.1.3 + trap-instructions.yaml AP-9)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILL_MARKETS_DIRNAME = "skill-markets"
SKILL_MARKETS = REPO_ROOT / SKILL_MARKETS_DIRNAME

# 实质性内容阈值:超过这个数才算"实质性变更"
SEMANTIC_LINE_THRESHOLD = 7

# Skill 一级"给人类看的说明性文档"白名单
SKILL_LEVEL_DOCS = {"README.md", "AGENTS.md", "CHANGELOG.md", "INDEX.md", "GUIDE.md"}

# 项目侧 5 项说明文档 + 注册表(注册表也算"项目侧文档",因为它登记 skill 列表)
PROJECT_LEVEL_DOCS = [
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "skill-markets/CAPABILITY-MAP.md",
    "SECURITY-MAP.md",
    "registry/skills.yaml",
]

# 哪些文件算 "skill 核心文件"(改动这些才需要触发同步检查)
SKILL_CORE_FILE_RE = re.compile(
    r"^skill-markets/(?P<pkg>[^/]+)/("
    r"SKILL\.md"
    r"|references/[^/]+\.md"
    r"|scripts/[^/]+"
    r"|agents/[^/]+\.md"
    r")$"
)

# Markdown 注释行判定 — 用纯字符串方法避开正则 + PowerShell 转义陷阱
# 规则: 整行 strip 后满足以下任一:
#   - 以 "#" 开头且 "#" 后第一个字符是空白(避免误判 "#hashtag")
#   - 以 "<!--" 开头并以 "-->" 结尾
def _is_md_comment_line(stripped: str) -> bool:
    if not stripped:
        return False
    if stripped.startswith("<!--") and stripped.endswith("-->"):
        return True
    if stripped.startswith("#"):
        # "#x" 无空格 → 不是注释(可能是 header)
        if len(stripped) > 1 and stripped[1] in (" ", "\t"):
            return True
        # 单 "#" 也算注释
        if len(stripped) == 1:
            return True
    return False

# SKILL.md frontmatter 关键字段(任一字段值变了 → 强制触发)
SKILL_FRONTMATTER_KEYS = {"name", "description", "version", "requires"}


# ─────────────────────────────────────────────────────────────────────────
# 工具函数 — 全部以 repo_root / skill_markets_dir 为参数,避免全局污染
# ─────────────────────────────────────────────────────────────────────────

def _run_git(*args: str, cwd: Path) -> str:
    """调用 git,返回 stdout(去末尾换行);失败抛 RuntimeError。"""
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd),
        creationflags=creationflags,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} 失败 (exit {result.returncode}): {result.stderr.strip()}"
        )
    return result.stdout.rstrip("\n")


def _diff_cached_files(repo_root: Path) -> List[str]:
    """返回 staged 文件列表(去掉空行,统一正斜杠)。"""
    out = _run_git("diff", "--cached", "--name-only", cwd=repo_root)
    return [line.strip().replace("\\", "/") for line in out.split("\n") if line.strip()]


def _diff_cached_lines(repo_root: Path, filepath: str) -> List[Tuple[str, str]]:
    """返回 staged 单文件的行级 diff,格式: [(marker, content), ...].

    marker ∈ {'+', '-', ' '}。-U0 让上下文为 0 行,只保留真正增删的行。
    """
    out = _run_git("diff", "--cached", "-U0", "--", filepath, cwd=repo_root)
    pairs: List[Tuple[str, str]] = []
    for line in out.split("\n"):
        if not line:
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        marker = line[0]
        if marker in ("+", "-", " "):
            content = line[1:]
            pairs.append((marker, content))
    return pairs


def _is_comment_or_blank(marker: str, content: str, filetype: str) -> bool:
    """判定一行是否属于"纯注释 / 空行"(不算语义)。"""
    if marker != "+":
        return False
    stripped = content.strip()
    if not stripped:
        return True
    if filetype == "md" and _is_md_comment_line(stripped):
        return True
    # py / 其他:暂不排除注释(本门禁只关心"实质新增内容",py 注释仍可能被当成语义 — 保守策略)
    return False


def _classify_filetype(filepath: str) -> str:
    """粗略分类文件:md / py / other。"""
    if filepath.endswith(".md"):
        return "md"
    if filepath.endswith(".py"):
        return "py"
    return "other"


def _count_semantic_lines(repo_root: Path, filepath: str) -> int:
    """统计某个文件的 staged 新增行中,真正算"语义"的行数。

    排除规则(完全按用户拍板):
      - 空行
      - 纯 MD 注释(`# ...` 或 HTML `<!-- ... -->`)
      - "纯格式" = 本实现不专门处理,因 .md 注释已覆盖大部分"非语义"
    """
    filetype = _classify_filetype(filepath)
    pairs = _diff_cached_lines(repo_root, filepath)
    sem = 0
    for marker, content in pairs:
        if _is_comment_or_blank(marker, content, filetype):
            continue
        sem += 1
    return sem


def _parse_frontmatter_from_text(text: str) -> Dict[str, str]:
    """极简 YAML frontmatter 解析 — 只支持 name: / description: / version: / requires: 顶层字段。"""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end].lstrip("\n")
    out: Dict[str, str] = {}
    current_key: str | None = None
    for raw in block.split("\n"):
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(.*)$", raw)
        if m:
            current_key = m.group(1)
            val = m.group(2).strip()
            val = re.sub(r"\s+#.*$", "", val).strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            out[current_key] = val
        elif current_key and raw.startswith((" ", "\t")):
            out[current_key] += " " + raw.strip()
    return {k: v.strip() for k, v in out.items() if k in SKILL_FRONTMATTER_KEYS}


def _parse_frontmatter(skill_md: Path) -> Dict[str, str]:
    if not skill_md.exists():
        return {}
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    return _parse_frontmatter_from_text(text)


def _safe_git_show(repo_root: Path, ref_path: str) -> str:
    """读 git <ref>:<path> 内容;失败返回空串。"""
    try:
        return _run_git("show", ref_path, cwd=repo_root)
    except RuntimeError:
        return ""


def _frontmatter_changed(repo_root: Path, pkg: str) -> bool:
    """若 SKILL.md staged 版本 vs HEAD 的 frontmatter 关键字段值变了 → True。"""
    skill_md_rel = f"skill-markets/{pkg}/SKILL.md"
    skill_md_abs = repo_root / skill_md_rel
    if not skill_md_abs.exists():
        return False
    head_text = _safe_git_show(repo_root, f"HEAD:{skill_md_rel}")
    head_fm = _parse_frontmatter_from_text(head_text)
    staged_fm = _parse_frontmatter(skill_md_abs)
    for key in SKILL_FRONTMATTER_KEYS:
        if head_fm.get(key, "") != staged_fm.get(key, ""):
            return True
    return False


def _skill_level_docs_exist(skill_markets_dir: Path, pkg: str) -> List[str]:
    """返回该 skill 一级目录下"实际存在的"人类入口文档(相对 skill_markets_dir)。"""
    skill_dir = skill_markets_dir / pkg
    if not skill_dir.exists():
        return []
    out: List[str] = []
    for doc_name in SKILL_LEVEL_DOCS:
        candidate = skill_dir / doc_name
        if candidate.exists() and candidate.is_file():
            out.append(f"{SKILL_MARKETS_DIRNAME}/{pkg}/{doc_name}")
    return out


# ─────────────────────────────────────────────────────────────────────────
# 主逻辑(接受 repo_root / skill_markets_dir)
# ─────────────────────────────────────────────────────────────────────────

def _collect_triggered_pkgs(
    staged_files: List[str], repo_root: Path
) -> Set[str]:
    """从 staged 文件列表中,计算"哪些 pkg 触发文档同步检查"。

    触发条件(任一):
      1. 核心文件(SKILL.md / references/*.md / scripts/* / agents/*.md)语义行 > 7
      2. SKILL.md frontmatter 关键字段变更
    """
    triggered: Set[str] = set()
    by_pkg: Dict[str, List[str]] = {}
    for f in staged_files:
        m = SKILL_CORE_FILE_RE.match(f)
        if not m:
            continue
        by_pkg.setdefault(m.group("pkg"), []).append(f)

    for pkg, files in by_pkg.items():
        total_sem = 0
        for f in files:
            total_sem += _count_semantic_lines(repo_root, f)
        fm_changed = _frontmatter_changed(repo_root, pkg)
        if total_sem > SEMANTIC_LINE_THRESHOLD or fm_changed:
            triggered.add(pkg)
    return triggered


def _check_sync_for_pkg(
    pkg: str,
    staged_set: Set[str],
    skill_markets_dir: Path,
) -> List[str]:
    """对单个触发的 pkg,找出"未同步的文档",返回清单(空 = 全部已同步)。"""
    missing: List[str] = []

    # (a) 项目侧 5 项 + 注册表
    for doc in PROJECT_LEVEL_DOCS:
        if doc not in staged_set:
            missing.append(f"[项目侧未同步] {doc}")

    # (b) skill 一级人类入口文档(仅检查当前存在的)
    for skill_doc_rel in _skill_level_docs_exist(skill_markets_dir, pkg):
        if skill_doc_rel not in staged_set:
            missing.append(f"[skill 一级未同步] {skill_doc_rel}")

    return missing


def run_main(repo_root: Path) -> int:
    """主入口 — 读 git diff --cached,检查同步。"""
    repo_root = repo_root.resolve()
    skill_markets_dir = repo_root / SKILL_MARKETS_DIRNAME
    if not (repo_root / ".git").exists() and not (
        repo_root / ".git"  # 不存在也无妨,git 命令会抛错
    ):
        pass

    staged_files = _diff_cached_files(repo_root)
    staged_set = set(staged_files)
    triggered = _collect_triggered_pkgs(staged_files, repo_root)

    print(f"🔍 doc-sync-guard: staged {len(staged_files)} 文件")
    print(f"   触发文档同步的 pkg: {sorted(triggered) if triggered else '(无)'}")

    if not triggered:
        print("✅ PASS — 无 skill 触发文档同步检查")
        return 0

    all_missing: Dict[str, List[str]] = {}
    for pkg in sorted(triggered):
        missing = _check_sync_for_pkg(pkg, staged_set, skill_markets_dir)
        if missing:
            all_missing[pkg] = missing

    if not all_missing:
        print(f"✅ PASS — {len(triggered)} 个 pkg 全部同步")
        return 0

    print("\n❌ BLOCK — 以下 pkg 改动后未同步文档:")
    for pkg, miss_list in all_missing.items():
        print(f"\n  📦 skill-markets/{pkg}/:")
        for m in miss_list:
            print(f"     - {m}")
    print(
        "\n🛠  修复:\n"
        "   1. 同步更新相应文档(项目侧 README/AGENTS/CHANGELOG/CAPABILITY-MAP/SECURITY-MAP/registry/skills.yaml\n"
        "      + skill 一级 README/AGENTS/CHANGELOG/INDEX/GUIDE)\n"
        "   2. 或用 `git commit --no-verify` 绕过(不推荐,失同步会污染下游)\n"
    )
    return 1


# ─────────────────────────────────────────────────────────────────────────
# Self-test (单元测试专用 — 构造临时 git 仓库)
# ─────────────────────────────────────────────────────────────────────────

def _make_tmp_repo() -> Path:
    """创建临时 git 仓库。"""
    tmp = Path(tempfile.mkdtemp(prefix="doc-sync-test-"))
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0

    def _git(*args: str) -> None:
        r = subprocess.run(
            ["git", *args],
            cwd=str(tmp),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creationflags,
        )
        if r.returncode != 0:
            raise RuntimeError(f"git {args} failed: {r.stderr}")

    _git("init", "-q")
    _git("config", "user.email", "test@test.local")
    _git("config", "user.name", "test")
    _git("config", "core.autocrlf", "false")
    (tmp / "skill-markets").mkdir()
    (tmp / "registry").mkdir()
    return tmp


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _git_in(tmp: Path, *args: str) -> str:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
    r = subprocess.run(
        ["git", *args],
        cwd=str(tmp),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed in {tmp}: {r.stderr}")
    return r.stdout


def _setup_pure_skill(tmp: Path) -> None:
    """基础仓库 + 一个 demo skill + 所有项目侧文档,先做一次空 commit。"""
    fm = textwrap.dedent("""\
        ---
        name: demo-skill
        description: self test demo skill
        version: 1.0.0
        ---

        # Demo Skill
        Original content.
    """)
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", fm)
    _write(tmp / "skill-markets" / "demo-skill" / "README.md", "# Demo README\n")
    _write(tmp / "skill-markets" / "demo-skill" / "AGENTS.md", "# Demo AGENTS\n")
    _write(tmp / "README.md", "# Root\n")
    _write(tmp / "AGENTS.md", "# Agents\n")
    _write(tmp / "CHANGELOG.md", "# Changelog\n")
    _write(tmp / "skill-markets" / "CAPABILITY-MAP.md", "# CAP\n")
    _write(tmp / "SECURITY-MAP.md", "# SEC\n")
    _write(tmp / "registry" / "skills.yaml", "version: 1.0.0\nskills: []\n")
    _git_in(tmp, "add", ".")
    _git_in(tmp, "commit", "-q", "-m", "init")


def _selftest_a_substantial_blocks(tmp: Path) -> None:
    """Case A: SKILL.md 改 8 行实质语义 + 文档未同步 → BLOCK。"""
    _setup_pure_skill(tmp)
    new = textwrap.dedent("""\
        ---
        name: demo-skill
        description: self test demo skill
        version: 1.0.0
        ---

        # Demo Skill
        Original content but with extra sem lines.
        Adding line two for the substantial change test.
        And three more lines to push past the threshold.
        Plus four more lines for clarity.
        Five lines to be sure.
        Six lines.
        Seven lines.
        Eight lines now.
        Nine extra.
    """)
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", new)
    _git_in(tmp, "add", "skill-markets/demo-skill/SKILL.md")


def _selftest_b_comment_only_passes(tmp: Path) -> None:
    """Case B: SKILL.md 只改 8 行 MD 注释 → 不触发 → PASS。"""
    _setup_pure_skill(tmp)
    base = (tmp / "skill-markets" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
    extra = "\n" + "\n".join([f"# comment line {i}" for i in range(8)])
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", base + extra)
    _git_in(tmp, "add", "skill-markets/demo-skill/SKILL.md")


def _selftest_c_blank_only_passes(tmp: Path) -> None:
    """Case C: SKILL.md 只改 8 行空行 → 不触发 → PASS。"""
    _setup_pure_skill(tmp)
    base = (tmp / "skill-markets" / "demo-skill" / "SKILL.md").read_text(encoding="utf-8")
    extra = "\n" + "\n".join(["" for _ in range(8)])
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", base + extra)
    _git_in(tmp, "add", "skill-markets/demo-skill/SKILL.md")


def _selftest_d_frontmatter_blocks(tmp: Path) -> None:
    """Case D: SKILL.md frontmatter description 改 1 行 + README 未同步 → BLOCK。

    同时 stage AGENTS.md(说明 skill 一级人类文档的 AGENTS 已同步)— 但 README 没动 → 仍 BLOCK。
    """
    _setup_pure_skill(tmp)
    new = textwrap.dedent("""\
        ---
        name: demo-skill
        description: self test demo skill — UPDATED
        version: 1.0.0
        ---

        # Demo Skill
        Original content.
    """)
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", new)
    _write(tmp / "skill-markets" / "demo-skill" / "AGENTS.md", "# Demo AGENTS\nupdated\n")
    _git_in(tmp, "add", "skill-markets/demo-skill/SKILL.md", "skill-markets/demo-skill/AGENTS.md")


def _selftest_e_substantial_with_all_synced_passes(tmp: Path) -> None:
    """Case E: SKILL.md 改 8 行实质 + 全部项目侧 + skill 一级 README + AGENTS 同步 → PASS。"""
    _setup_pure_skill(tmp)
    new = textwrap.dedent("""\
        ---
        name: demo-skill
        description: self test demo skill
        version: 1.0.0
        ---

        # Demo Skill
        line one update.
        line two update.
        line three update.
        line four update.
        line five update.
        line six update.
        line seven update.
        line eight update.
        line nine update.
    """)
    _write(tmp / "skill-markets" / "demo-skill" / "SKILL.md", new)
    # 同步所有项目侧 6 项
    _write(tmp / "README.md", "# Root updated\n")
    _write(tmp / "AGENTS.md", "# Agents updated\n")
    _write(tmp / "CHANGELOG.md", "# Changelog updated\n")
    _write(tmp / "skill-markets" / "CAPABILITY-MAP.md", "# CAP updated\n")
    _write(tmp / "SECURITY-MAP.md", "# SEC updated\n")
    _write(tmp / "registry" / "skills.yaml", "version: 1.0.0\nskills: []\nupdated: 1\n")
    # 同步 skill 一级 README + AGENTS(其他 skill 一级文档不存在 → 跳过)
    _write(tmp / "skill-markets" / "demo-skill" / "README.md", "# Demo README updated\n")
    _write(tmp / "skill-markets" / "demo-skill" / "AGENTS.md", "# Demo AGENTS updated\n")
    _git_in(tmp, "add", "-A")


def _selftest_f_excluded_subdir_ignored(tmp: Path) -> None:
    """Case F: skill 内子目录(如 references/)的 README 改 → 不算 skill 一级 → 不触发。

    但本 case 同时改了 SKILL.md frontmatter description — 这条还是会触发。
    所以我们刻意只改 frontmatter 的一个无关紧要的字段(实际 description 不变)→ 仍应不触发。

    实现方式:不碰 SKILL.md 任何字段,只动 references/README.md,且不动其他 — 但 SKILL_CORE_FILE_RE
    匹配 references/*.md 会被算成核心文件,所以这里要构造 "references/*.md 改动语义行 ≤ 7" + frontmatter 不变。

    更简单的方案:本 case 只改 references/README.md 加 1 行内容,且让 SKILL.md 0 改动。
    因 references/README.md 改动 < 8 行 → 不触发 → PASS。
    """
    _setup_pure_skill(tmp)
    # 加一个 references/README.md,改 1 行
    _write(
        tmp / "skill-markets" / "demo-skill" / "references" / "README.md",
        "# references README\none line.\n",
    )
    _git_in(tmp, "add", "skill-markets/demo-skill/references/README.md")


def _self_test_case(
    name: str, expect: int, setup_fn: Callable[[Path], None]
) -> bool:
    """单 case — 造临时仓库 → setup → 跑守卫 → 验证 exit code。"""
    tmp = _make_tmp_repo()
    try:
        setup_fn(tmp)
        code = run_main(tmp)
        ok = code == expect
        marker = "✅" if ok else "❌"
        print(f"  {marker} {name} (期望 exit {expect}, 实际 exit {code})")
        return ok
    except Exception as e:
        print(f"  ❌ {name} — 异常: {e}")
        return False
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)


def _self_test() -> int:
    """跑全套反例 + 边界用例,返回 PASS 数 == len(cases) → 0。"""
    print("━━━ doc-sync-guard self-test ━━━")
    cases: List[Tuple[str, int, Callable[[Path], None]]] = [
        ("A: SKILL 8 行语义 + 缺同步 → BLOCK", 1, _selftest_a_substantial_blocks),
        ("B: SKILL 只改 8 行注释 → PASS", 0, _selftest_b_comment_only_passes),
        ("C: SKILL 只改 8 行空行 → PASS", 0, _selftest_c_blank_only_passes),
        ("D: SKILL frontmatter 改 + README 缺 → BLOCK", 1, _selftest_d_frontmatter_blocks),
        ("E: SKILL 8 行 + 全部同步 → PASS", 0, _selftest_e_substantial_with_all_synced_passes),
        ("F: 子目录 README 不算 skill 一级 → 不触发 → PASS", 0, _selftest_f_excluded_subdir_ignored),
    ]
    ok = sum(_self_test_case(name, expect, fn) for name, expect, fn in cases)
    print(f"\n  汇总: {ok}/{len(cases)} 通过")
    return 0 if ok == len(cases) else 1


# ─────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="技能文档同步门禁 (pre-commit Step 7)",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="跑反例自检(不读真实 git diff,造临时仓库)",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="REPO_ROOT 路径覆盖(测试用,默认脚本所在仓库根)",
    )
    # 兼容 guard-router.mjs 调用风格:它会传 skill 路径作为 positional argv,
    # 我们忽略这些额外参数(横切守卫不接受 skill 名 — 它跑全仓库)。
    args, _unknown = parser.parse_known_args()

    if args.self_test:
        return _self_test()

    repo_root = Path(args.repo_root).resolve()
    return run_main(repo_root)


if __name__ == "__main__":
    sys.exit(main())