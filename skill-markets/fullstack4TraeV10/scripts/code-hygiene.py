#!/usr/bin/env python3
"""code-hygiene.py — 编写后立即检查代码卫生

检测项:
  - 单文件 > 800 行 → 🛑 REJECT
  - 单函数 > 50 行 → 🛑 REJECT
  - 圈复杂度 > 15 → 🛑 REJECT

用法:
  python scripts/code-hygiene.py --changed-files [--max-lines 800] [--max-fn-lines 50] [--max-complexity 15]
  python scripts/code-hygiene.py --path {dir_or_file}
"""

import argparse
import re
import sys
from pathlib import Path

# 支持的文件类型
SUPPORTED_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".vue", ".go", ".rs", ".java", ".cs"}

# 函数定义模式（简化版，按语言）
FN_PATTERNS = {
    ".py": re.compile(r"^(?:async\s+)?def\s+(\w+)\s*\("),
    ".ts": re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(\w+)\s*\([^)]*\)\s*[:{]"),
    ".tsx": re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(\w+)\s*\([^)]*\)\s*[:{]"),
    ".js": re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(\w+)\s*\([^)]*\)\s*[:{]"),
    ".jsx": re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(\w+)\s*\([^)]*\)\s*[:{]"),
    ".vue": re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(\w+)\s*\([^)]*\)\s*[:{]"),
    ".go": re.compile(r"^func\s+(\w+)\s*\("),
    ".rs": re.compile(r"^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\("),
    ".java": re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*[{;]"),
    ".cs": re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)?(\w+)\s*\([^)]*\)\s*[{;]"),
}

# 圈复杂度计算（粗略版：统计分支关键字）
COMPLEXITY_KEYWORDS = re.compile(r"\b(if|elif|else if|for|while|case|catch|&&|\|\||\?)\b")


def count_lines(path: Path) -> int:
    """统计文件行数（跳过空行）"""
    return sum(1 for line in path.read_text(encoding="utf-8", errors="ignore").splitlines() if line.strip())


def check_function_lengths(path: Path, content: str, max_fn_lines: int) -> list[str]:
    """检测函数体行数"""
    ext = path.suffix
    pattern = FN_PATTERNS.get(ext)
    if not pattern:
        return []

    lines = content.splitlines()
    errors = []
    fn_start = None
    fn_name = None
    indent_level = None

    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            # 结束上一个函数
            if fn_start is not None and indent_level is not None:
                fn_len = i - fn_start
                if fn_len > max_fn_lines:
                    errors.append(f"{path}:{fn_start+1}: 函数 '{fn_name}' = {fn_len} 行 > {max_fn_lines}")

            # 开始新函数
            fn_start = i
            fn_name = match.group(1) or match.group(2) or "anonymous"
            # 计算缩进
            indent_level = len(line) - len(line.lstrip())

    # 最后一个函数
    if fn_start is not None:
        fn_len = len(lines) - fn_start
        if fn_len > max_fn_lines:
            errors.append(f"{path}:{fn_start+1}: 函数 '{fn_name}' = {fn_len} 行 > {max_fn_lines}")

    return errors


def check_complexity(path: Path, content: str, max_complexity: int) -> list[str]:
    """检测圈复杂度（粗略：每函数分支关键字计数）"""
    ext = path.suffix
    pattern = FN_PATTERNS.get(ext)
    if not pattern:
        return []

    lines = content.splitlines()
    errors = []
    fn_start = None
    fn_name = None

    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            # 结束上一个函数
            if fn_start is not None:
                fn_content = "\n".join(lines[fn_start:i])
                complexity = 1 + len(COMPLEXITY_KEYWORDS.findall(fn_content))
                if complexity > max_complexity:
                    errors.append(f"{path}:{fn_start+1}: 函数 '{fn_name}' 圈复杂度 = {complexity} > {max_complexity}")

            fn_start = i
            fn_name = match.group(1) or match.group(2) or "anonymous"

    return errors


def check_file(path: Path, max_lines: int, max_fn_lines: int, max_complexity: int) -> list[str]:
    """检查单个文件"""
    if path.suffix not in SUPPORTED_EXT:
        return []

    errors = []

    # 1. 文件行数
    line_count = count_lines(path)
    if line_count > max_lines:
        errors.append(f"{path}: 文件 {line_count} 行 > {max_lines}")

    # 2. 函数行数
    content = path.read_text(encoding="utf-8", errors="ignore")
    errors.extend(check_function_lengths(path, content, max_fn_lines))

    # 3. 圈复杂度
    errors.extend(check_complexity(path, content, max_complexity))

    return errors


def get_changed_files(project_root: Path) -> list[Path]:
    """获取 git 变更的文件（排除已删除、不存在或非代码文件）"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []

    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # porcelain 格式: "XY filename" — 前两位是状态码，第三位起是路径
        status_code = line[:2]
        rel_path = line[3:].strip()
        # 任一状态为 D (已删除) 直接跳过
        if "D" in status_code:
            continue
        full_path = project_root / rel_path
        # 防御：磁盘不存在也跳过（rename、untracked 等边界）
        if not full_path.is_file():
            continue
        if full_path.suffix in SUPPORTED_EXT:
            files.append(full_path)
    return files


def get_diff_files(project_root: Path, base_ref: str = "HEAD") -> list[Path]:
    """基于 git diff 只获取相对 base_ref 新增/修改的文件（排除已删除）"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMRT", base_ref],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []

    files: list[Path] = []
    for f in result.stdout.splitlines():
        if not f.strip():
            continue
        full_path = project_root / f
        if not full_path.is_file():
            continue
        if full_path.suffix in SUPPORTED_EXT:
            files.append(full_path)
    return files


def main():
    parser = argparse.ArgumentParser(description="代码卫生硬门禁检查")
    parser.add_argument("--changed-files", action="store_true", help="检查 git 变更的文件")
    parser.add_argument(
        "--diff-base",
        help="只校验 git diff 新增/修改的文件（base ref，如 HEAD 或 main）。"
             "与 --changed-files 不同：--changed-files = 工作区全部变更（staged+unstaged），"
             "--diff-base = 基于指定 ref 的 diff。",
    )
    parser.add_argument("--path", type=str, help="检查指定路径（文件或目录）")
    parser.add_argument("--max-lines", type=int, default=800, help="单文件最大行数")
    parser.add_argument("--max-fn-lines", type=int, default=50, help="单函数最大行数")
    parser.add_argument("--max-complexity", type=int, default=15, help="圈复杂度上限")
    parser.add_argument("--project-root", type=str, default=".", help="项目根")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    # 收集目标文件
    targets: list[Path] = []
    if args.diff_base:
        targets = get_diff_files(project_root, args.diff_base)
    elif args.changed_files:
        targets = get_changed_files(project_root)
    elif args.path:
        p = Path(args.path).resolve()
        if p.is_file():
            targets = [p]
        elif p.is_dir():
            for ext in SUPPORTED_EXT:
                targets.extend(p.rglob(f"*{ext}"))
    else:
        parser.error("需要 --changed-files / --diff-base / --path 之一")

    if not targets:
        print("✅ 无目标文件，跳过检查")
        sys.exit(0)

    # 执行检查
    all_errors = []
    for path in targets:
        all_errors.extend(check_file(path, args.max_lines, args.max_fn_lines, args.max_complexity))

    # 输出结果
    if all_errors:
        print(f"🛑 code-hygiene 检查失败：{len(all_errors)} 项问题\n")
        for err in all_errors:
            print(f"  - {err}")
        print(f"\n修复后再提交。任一 FAIL = 🛑 REJECT")
        sys.exit(1)
    else:
        print(f"✅ code-hygiene 通过：{len(targets)} 个文件全部满足卫生要求")
        sys.exit(0)


if __name__ == "__main__":
    main()