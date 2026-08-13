#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install-husky.py — 将 scaffold 内 gates/*.sh 复制到目标项目的 .husky/

特性：
  - 支持 registry/stacks.yaml 注册的所有 stack（nodejs / python / go / java-maven）
  - --dry-run 预演（R-2 必走）
  - Windows 兼容（chmod 退化到提示，不抛异常）
  - 目标 ≠ 源 校验（R-2）

用法：
    python install-husky.py --stack nodejs --target <project-path> [--dry-run]
    python install-husky.py --stack python --target . --dry-run

退出码：
    0  成功（或 dry-run 成功 / 源文件缺失 WARN 跳过）
    2  参数错误

依赖：仅 Python 3.8+ 标准库；可选 PyYAML（缺失时使用硬编码 stack 注册表）
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 颜色（colorama 可选；与 gate-check.py 风格对齐）
try:
    from colorama import init as _colorama_init, Fore, Style  # type: ignore
    _HAS_COLORAMA = True
    _colorama_init()
except Exception:  # pragma: no cover
    _HAS_COLORAMA = False

    class _Dummy:
        def __getattr__(self, _name: str) -> str:
            return ""

    Fore = _Dummy()
    Style = _Dummy()


EXIT_OK = 0
EXIT_USAGE = 2

GATE_FILES = ("pre-commit", "pre-push")

# 与 registry/stacks.yaml 同步；yaml 缺失时兜底
HARDCODED_STACKS: Dict[str, str] = {
    "nodejs": "scaffolds/nodejs/files/gates",
    "python": "scaffolds/python/files/gates",
    "go": "scaffolds/go/files/gates",
    "java-maven": "scaffolds/java-maven/files/gates",
}

SCRIPT_DIR = Path(__file__).resolve(strict=False)
# install-husky.py 位于 <SKILL_ROOT>/scripts/，所以 SKILL_ROOT = SCRIPT_DIR.parent.parent
SKILL_ROOT = SCRIPT_DIR.parent.parent  # skill-markets/agent-dev-control-kit


def _color(text: str, kind: str) -> str:
    """与 gate-check.py 同款 emoji 前缀；不依赖 colorama。"""
    if _HAS_COLORAMA:
        if kind == "ok":
            return f"{Fore.GREEN}✅{Style.RESET_ALL} {text}"
        if kind == "warn":
            return f"{Fore.YELLOW}⚠️{Style.RESET_ALL} {text}"
        if kind == "err":
            return f"{Fore.RED}🛑{Style.RESET_ALL} {text}"
        return f"{Fore.CYAN}ℹ️{Style.RESET_ALL} {text}"
    icons = {"ok": "✅", "warn": "⚠️ ", "err": "🛑", "info": "ℹ️ "}
    return f"{icons.get(kind, 'ℹ️ ')} {text}"


def log_ok(msg: str) -> None:
    print(_color(msg, "ok"))


def log_warn(msg: str) -> None:
    print(_color(msg, "warn"), file=sys.stderr)


def log_err(msg: str) -> None:
    print(_color(msg, "err"), file=sys.stderr)


def log_info(msg: str) -> None:
    print(_color(msg, "info"))


def load_stacks() -> Dict[str, str]:
    """从 registry/stacks.yaml 读取 stack 注册表；失败兜底硬编码。"""
    yaml_path = SKILL_ROOT / "registry" / "stacks.yaml"
    if not yaml_path.is_file():
        log_warn(f"未找到 {yaml_path}，使用硬编码 stack 注册表")
        return dict(HARDCODED_STACKS)

    try:
        import yaml  # type: ignore
    except ImportError:
        log_warn("PyYAML 未安装，使用硬编码 stack 注册表")
        return dict(HARDCODED_STACKS)

    try:
        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        stacks_raw = data.get("stacks") or []
        result: Dict[str, str] = {}
        for entry in stacks_raw:
            sid = entry.get("id")
            sc = entry.get("scaffold")
            if sid and sc:
                # 路径是相对 skill 根的；拼到 files/gates/
                result[str(sid)] = f"{sc}/files/gates"
        return result or dict(HARDCODED_STACKS)
    except Exception as e:  # pragma: no cover
        log_warn(f"读取 stacks.yaml 失败 ({e})，回退硬编码")
        return dict(HARDCODED_STACKS)


def resolve_target_safety(target_arg: str) -> Path:
    """R-2 铁律：使用 strict=False 拿到绝对路径，绝不解 symlink。"""
    raw = Path(target_arg)
    # strict=False：路径不存在时不抛异常
    abs_target = raw.resolve(strict=False)
    abs_target_str = str(abs_target)

    # 校验：目标不能指向 skill 源（防止把 .husky 写回 skill 目录）
    skill_root_str = str(SKILL_ROOT.resolve(strict=False))
    if abs_target_str == skill_root_str:
        raise ValueError(
            f"R-2 violation: 目标等于 skill 源 ({skill_root_str})，拒绝写入"
        )
    if abs_target_str.startswith(skill_root_str + os.sep):
        raise ValueError(
            f"R-2 violation: 目标在 skill 源目录内 ({skill_root_str})，拒绝写入"
        )
    # 校验：目标路径字段不能是 .husky（防止目标本身是 .husky 目录导致混淆）
    parts = abs_target.parts
    if ".husky" in parts:
        log_warn(f"目标路径含 .husky 字段：{abs_target_str}（按本意继续）")

    return abs_target


def find_source_dir(stack_id: str, stacks: Dict[str, str]) -> Optional[Path]:
    """查找 scaffold 内 gates 源目录。"""
    rel = stacks.get(stack_id)
    if not rel:
        return None
    src = SKILL_ROOT / rel
    if src.is_dir():
        return src
    return None


def safe_chmod(path: Path) -> Tuple[bool, str]:
    """Windows 兼容的 chmod；失败返回 (False, 提示)。"""
    try:
        os.chmod(path, 0o755)
        return True, "ok"
    except OSError as e:
        msg = (
            f"chmod +x 失败（{e.__class__.__name__}: {e}）。"
            "Windows 下请改用 `git config core.hooksPath .husky` 或在 WSL 内运行。"
        )
        return False, msg


def copy_gate(src_file: Path, dst_file: Path, dry_run: bool) -> bool:
    """复制单个 gate 脚本 + chmod +x；dry-run 只打印。"""
    if dry_run:
        log_info(f"[dry-run] 将复制 {src_file} → {dst_file}")
        log_info(f"[dry-run] 将 chmod +x {dst_file}")
        return True

    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_file, dst_file)
    ok, msg = safe_chmod(dst_file)
    if not ok:
        log_warn(msg)
        # 退化：内容已复制成功，chmod 失败不算致命
        return True
    return True


def install(stack: str, target_arg: str, dry_run: bool) -> int:
    """主入口：安装一组 gates 到目标 .husky/。"""
    stacks = load_stacks()
    src_dir = find_source_dir(stack, stacks)
    if src_dir is None:
        log_warn(f"stack '{stack}' 未注册或 scaffold 目录缺失，跳过")
        log_warn(f"已注册 stacks: {', '.join(sorted(stacks.keys()))}")
        return EXIT_OK  # WARN 跳过不算错

    try:
        target = resolve_target_safety(target_arg)
    except ValueError as e:
        log_err(str(e))
        return EXIT_USAGE

    husky_dir = target / ".husky"

    if not dry_run:
        husky_dir.mkdir(parents=True, exist_ok=True)

    log_info(f"stack       = {stack}")
    log_info(f"source dir  = {src_dir}")
    log_info(f"target .husky = {husky_dir}")
    if dry_run:
        log_info("模式 = dry-run（不写入任何文件）")

    installed = 0
    for name in GATE_FILES:
        src_file = src_dir / f"{name}.sh"
        dst_file = husky_dir / name
        if not src_file.is_file():
            log_warn(f"源文件缺失，跳过: {src_file}")
            continue
        if copy_gate(src_file, dst_file, dry_run):
            installed += 1
            if not dry_run:
                log_ok(f"已安装 {dst_file}")

    log_ok(f"完成：安装 {installed} 个 gate(s)（stack={stack}, dry_run={dry_run}）")
    return EXIT_OK


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="install-husky.py",
        description="将 scaffold 内 gates/*.sh 安装到目标项目的 .husky/ 目录",
    )
    parser.add_argument(
        "--stack",
        default="nodejs",
        help="技术栈 ID，默认 nodejs。可选：nodejs / python / go / java-maven",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="目标项目根目录路径（将在其下创建 .husky/）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将执行的操作，不实际写文件（R-2 预演）",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        return install(args.stack, args.target, args.dry_run)
    except KeyboardInterrupt:
        log_err("用户中断")
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
