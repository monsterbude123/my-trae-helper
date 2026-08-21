#!/usr/bin/env python3
"""
ai-testmate 工作空间自动探测

策略:从 cwd 向上递归找第一个含 .agents/.env 的目录,作为 workspace 根。

5 层优先级:
  1. env 显式注入 TESTMATE_WORKSPACE_ROOT(强制覆盖)
  2. cwd 的 .agents/.env 直接存在
  3. cwd 父目录的 .agents/.env(向上 1 层)
  4. cwd 向上递归,直到 filesystem root(默认上限 10 层防无限循环)
  5. fallback:返回 cwd 本身 + WARN(让上层报错提示用户)

返回:
  workspace_root: pathlib.Path(可能不存在,仅作标识)
  env_file:       pathlib.Path | None
  detected_mode:  "explicit" | "cwd" | "ancestor" | "fallback"
"""

import argparse
import os
import pathlib
import sys


MAX_ANCESTOR_DEPTH = 10  # 防爆栈


def detect(start: pathlib.Path, explicit_root: str | None = None) -> tuple:
    """
    探测工作空间根
    返回 (workspace_root, env_file, detected_mode)
    """
    start = start.resolve()

    # 1. 显式 env 注入
    if explicit_root:
        root = pathlib.Path(explicit_root).resolve()
        env = root / ".agents" / ".env"
        return root, env if env.exists() else None, "explicit"

    # 2-4. cwd / 父目录 / 向上递归
    cur = start
    for depth in range(MAX_ANCESTOR_DEPTH + 1):
        env = cur / ".agents" / ".env"
        if env.is_file():
            mode = "cwd" if depth == 0 else "ancestor"
            return cur, env, mode
        parent = cur.parent
        if parent == cur:  # 到达 filesystem root
            break
        cur = parent

    # 5. fallback:返回 cwd + warn
    return start, None, "fallback"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default=pathlib.Path.cwd(),
                        help="探测起点(默认 cwd)")
    parser.add_argument("--explicit-root", default=os.environ.get("TESTMATE_WORKSPACE_ROOT"),
                        help="env 显式注入覆盖")
    parser.add_argument("--json", action="store_true", help="输出 JSON(给 agent 调用)")
    parser.add_argument("--strict", action="store_true",
                        help="探测失败(无 .agents/.env)时 exit 2")
    args = parser.parse_args()

    root, env_file, mode = detect(pathlib.Path(args.start), args.explicit_root)

    if args.json:
        import json
        print(json.dumps({
            "workspace_root": str(root),
            "env_file": str(env_file) if env_file else None,
            "detected_mode": mode,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"workspace_root : {root}")
        print(f"env_file       : {env_file or '(未找到)'}")
        print(f"detected_mode  : {mode}")

    if args.strict and mode == "fallback":
        print(f"\n[FATAL] 未找到 .agents/.env,工作空间探测失败", file=sys.stderr)
        print(f"  探测起点:{args.start}", file=sys.stderr)
        print(f"  上限深度:{MAX_ANCESTOR_DEPTH} 层", file=sys.stderr)
        print(f"  建议:在项目根建 .agents/.env,或显式 TESTMATE_WORKSPACE_ROOT", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())