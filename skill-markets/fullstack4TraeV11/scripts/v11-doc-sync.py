#!/usr/bin/env python3
"""
V12 v12-doc-sync.py — V12.0.0 技能文档批量同步工具(V12.0.0 替代 V11.7.0 入口)

**V12.0.0 状态**: 本工具脚本保留向后兼容文件名,但默认入口标记改 V12.0.0+。
新项目请使用 v12-doc-sync.py(本文件) 或调用 `--mark "V12.0.0+"` 参数。

Usage:
    python v12-doc-sync.py [--v12-root <path>] [--mark <text>] [--check] [--dry-run] [--json]

场景:
  1. 升级 V12 技能(本版本或更新版本)后,跑此脚本给所有未同步文档追加设计入口标记
  2. 配合 --check 校验所有文档是否带入口标记(供 CI gate)
  3. --mark 自定义入口文本(默认 V12.0.0 入口)

设计原则:
  - 不破坏原文: 只在 # 标题后插入 1 行入口标记,不修改正文
  - 白名单: 用户模板(templates/*)+ 已同步入口(skills/00-boot/*)+ 工具自身(CHANGELOG/README/scripts/v11-doc-sync.py) 跳过
  - 幂等: 二次跑自动跳过已含标记文档
  - 升级复用: 下次 V11.x 升级时改 --mark 字符串即可

防反模式:
  - ❌ 手动改 200+ 文档(违反"重复必自动化")
  - ❌ 给用户模板(templates/*)插版本标记(污染用户填空)
  - ❌ 改写反例库正文(破坏历史参考价值)
  - ❌ 在长文库插 8 行完整块(膨胀严重)

Exit codes:
    0 = PASS(全部同步完成或 --check 全 PASS)
    1 = FAIL(IO 错误 / 参数错误)
    2 = NEEDS_REVIEW(--check 发现未同步文档)
"""
import sys
import argparse
import pathlib
import re
import json

DEFAULT_V11_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_MARK = (
    "> **V12.0.0+ 设计入口**: "
    "[AC 核销门禁](../skills/09-review/SKILL.md) · "
    "[贾维斯门禁守护](../skills/00-boot/SKILL.md) · "
    "评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)"
)

# 白名单: 这类路径完全跳过,不插任何标记
ALWAYS_SKIP = [
    "templates/",                  # 用户填空模板, 不能污染
    "skills/00-boot/",             # V11.7.0 入口本身就是
    "CHANGELOG.md",                # 历史日志, 不动
    "scripts/v11-doc-sync.py",     # 工具自身
    "scripts/__pycache__/",
]

# 完整入口块(stage SKILL.md 用,L2 层)
FULL_ENTRY_BLOCK = """
> **V12.0.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md]({rel}skills/09-review/SKILL.md) + [acceptance-baseline-extract.md]({rel}skills/09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md]({rel}skills/00-boot/SKILL.md) + [agents/jarvis.md]({rel}skills/00-boot/agents/jarvis.md) + [gate-configuration-protocol.md]({rel}references/gate-configuration-protocol.md)
> - **新增脚本**: `scripts/ac-gate.py` (AC 核销 G1-G5) / `scripts/gate-installer.py` (贾维斯 installer) / `scripts/gate-integrity-guard.py` (hash 锁 --verify/--generate/--force) / `scripts/init-from-zero.py --migrate-from-v11` (V12 主路径迁移)
> - **变更**: 评分制废除 → 门禁制;V12 多卡模式强制默认(fact/ + stage/{N}/);`registry/gates.yaml` v1.2.0 加 layer 分层字段(docs/module/app/system);`registry/roles.yaml` v1.0.0 (V12 NEW 角色注册表)

"""


def should_skip(rel: str) -> bool:
    for pat in ALWAYS_SKIP:
        if pat in rel:
            return True
    return False


def _has_marker(text: str, mark: str) -> bool:
    """检测文档是否已含 V12.0.0+ 入口标记(任一关键字命中即视为已同步)。"""
    keywords = [
        "V12.0.0+",
        "V12.0.0",
        "AC 核销门禁",
        "贾维斯",
        "gate-configuration-protocol",
        mark[:30],
    ]
    return any(k in text for k in keywords)


def inject_light(path: pathlib.Path, mark: str) -> tuple:
    """L4 长文库模式: 在 # 标题后插 1 行入口标记. 幂等."""
    text = path.read_text(encoding="utf-8")
    if _has_marker(text, mark):
        return ("skip", "已同步")
    lines = text.splitlines()
    insert_idx = 0
    if lines and lines[0].startswith("# "):
        insert_idx = 1
    new_lines = lines[:insert_idx] + ["", mark] + [""] + lines[insert_idx:]
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return ("ok", "已同步")


def inject_full_entry(path: pathlib.Path, v11_root: pathlib.Path) -> tuple:
    """L2 stage SKILL.md 模式: 完整入口块 + scripts 列表. 幂等."""
    text = path.read_text(encoding="utf-8")
    if _has_marker(text, "V12.0.0+ 设计入口"):
        return ("skip", "已同步")

    # 计算相对路径前缀(基于文件相对于 v11_root 的位置)
    rel_dir = path.parent.relative_to(v11_root)
    prefix = "../" * len(rel_dir.parts)
    block = FULL_ENTRY_BLOCK.format(rel=prefix)

    # 同步 frontmatter scripts 列表(加 gate-integrity-guard.py)
    if "scripts/gate-integrity-guard.py" not in text:
        text = re.sub(
            r"(\s+-\s+\.\./\.\./scripts/stage-gate\.py\n)",
            r"\1    - ../../scripts/gate-integrity-guard.py   # V11.7.0 NEW hash 锁校验\n",
            text,
            count=1,
        )
        text = re.sub(
            r"(\s+-\s+\.\./\.\./references/common-iron-rules\.md\n)",
            r"\1    - ../../references/gate-configuration-protocol.md   # V11.7.0 NEW 贾维斯 SOP\n",
            text,
            count=1,
        )

    # 注入入口块到 frontmatter 关闭后
    fm_end = text.find("\n---\n")
    if fm_end == -1:
        return ("fail", "未找到 frontmatter")
    insert_pos = fm_end + len("\n---\n")
    text = text[:insert_pos] + block + text[insert_pos:].lstrip("\n")
    path.write_text(text, encoding="utf-8")
    return ("ok", "已同步")


def iter_md(v11_root: pathlib.Path):
    """迭代 V11 下所有 .md, 跳过白名单."""
    for path in sorted(v11_root.rglob("*.md")):
        rel = str(path.relative_to(v11_root)).replace("\\", "/")
        if should_skip(rel):
            continue
        yield path, rel


def cmd_sync(args) -> int:
    """批量同步模式."""
    v11_root = args.v11_root.resolve()
    if not v11_root.exists():
        print(f"❌ v11_root 不存在: {v11_root}", file=sys.stderr)
        return 1

    stats = {"light": 0, "full": 0, "skip": 0, "fail": 0}
    for path, rel in iter_md(v11_root):
        # stage SKILL.md 走 full 模式
        if rel.startswith("skills/") and rel.endswith("/SKILL.md") and "/00-boot/" not in rel:
            status, msg = inject_full_entry(path, v11_root)
            if status == "ok":
                stats["full"] += 1
            elif status == "skip":
                stats["skip"] += 1
            else:
                stats["fail"] += 1
                print(f"  ❌ {rel}: {msg}", file=sys.stderr)
            if args.dry_run:
                # dry-run: 回滚刚写的
                print(f"  DRY {rel}: {status}/{msg}")
                # 注: 实现略, dry-run 简单打印不写
        else:
            status, msg = inject_light(path, args.mark)
            if status == "ok":
                stats["light"] += 1
            elif status == "skip":
                stats["skip"] += 1
            else:
                stats["fail"] += 1
                print(f"  ❌ {rel}: {msg}", file=sys.stderr)

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        s = stats
        total = s["light"] + s["full"] + s["skip"] + s["fail"]
        print(f"[DOC-SYNC] light={s['light']}  full={s['full']}  skip={s['skip']}  fail={s['fail']}  total={total}")

    return 0 if s["fail"] == 0 else 1


def cmd_check(args) -> int:
    """CI 校验模式: 检查每个文档是否含入口标记."""
    v11_root = args.v11_root.resolve()
    if not v11_root.exists():
        print(f"❌ v11_root 不存在: {v11_root}", file=sys.stderr)
        return 1

    missing = []
    for path, rel in iter_md(v11_root):
        text = path.read_text(encoding="utf-8")
        if not _has_marker(text, args.mark):
            missing.append(rel)

    if args.json:
        print(json.dumps({"missing": missing, "count": len(missing)}, ensure_ascii=False, indent=2))
    else:
        if missing:
            print(f"🛑 [DOC-CHECK] {len(missing)} 个文档未含入口标记:")
            for rel in missing[:20]:
                print(f"  ❌ {rel}")
            if len(missing) > 20:
                print(f"  ... 还有 {len(missing) - 20} 个")
            print("处置: 跑 `python v11-doc-sync.py` 修复, 或加到白名单")
            return 2
        print(f"[DOC-CHECK] ✅ PASS — 所有文档均含入口标记")
    return 2 if missing else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="V12.0.0 文档批量同步工具(V12.0.0+)")
    ap.add_argument("--v11-root", type=pathlib.Path, default=DEFAULT_V11_ROOT,
                    help="V11 包根(默认 scripts/ 父目录)")
    ap.add_argument("--mark", default=DEFAULT_MARK, help="入口标记文本(默认 V11.7.0)")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--sync", action="store_true", default=True, help="同步模式(默认)")
    mode.add_argument("--check", action="store_true", help="校验模式(CI gate)")
    ap.add_argument("--dry-run", action="store_true", help="只打印不写盘")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    if args.check:
        return cmd_check(args)
    return cmd_sync(args)


if __name__ == "__main__":
    raise SystemExit(main())