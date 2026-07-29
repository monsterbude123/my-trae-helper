"""
V8 → V9.2 项目迁移脚本。

用法:
  python scripts/migrate-v8-to-v9.py --project-root <项目路径>
  python scripts/migrate-v8-to-v9.py --project-root . --dry-run
  python scripts/migrate-v8-to-v9.py --project-root . --skip-hooks

策略:
  - V8 残留 → docs/bak_v8doc/（不删除，可回溯）
  - 只迁移 V9.2 关心的内容（specs 拍平 + state-card 转换 + hooks 升级）
  - Archive 检查但不修改（归档不可变）
  - 幂等安全，可重复执行
"""

import argparse
import shutil
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


# ─── 内部安装 hooks ──────────────────────────────────

def install_hooks(project_root: Path) -> list[str]:
    """内联 hooks 安装逻辑（不依赖 install-hooks.py 子进程）。"""
    skill_root = Path(__file__).resolve().parent.parent
    hooks_src = skill_root / "templates" / "hooks"
    scripts_src = skill_root / "templates" / "scripts"
    hooks_dst = project_root / ".trae" / "hooks"

    installed = []

    for name in [
        "session-start.py", "complexity-guard.py", "doc-sync-gate.py",
        "contract-gate.py", "spec-validate-hook.py", "auto-test.py",
        "drift-detect.py", "tasks-integrity.py",
    ]:
        src = hooks_src / name
        dst = hooks_dst / name
        if src.exists():
            hooks_dst.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)
                installed.append(f"hooks/{name}")

    json_src = hooks_src / "fullstack-hooks.json"
    json_dst = project_root / ".trae" / "hooks.json"
    if json_src.exists():
        copy_json = True
        if json_dst.exists():
            old = json_dst.read_text(encoding="utf-8")
            if ".ps1" not in old:
                copy_json = False
        if copy_json:
            shutil.copy2(json_src, json_dst)
            installed.append("hooks.json")

    for name in ["env-init.py", "render-cockpit.py", "log-agent-prompt.py"]:
        src = scripts_src / name
        dst = hooks_dst / name
        if src.exists():
            if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
                shutil.copy2(src, dst)
                installed.append(f"hooks/{name}")

    for old_ps1 in hooks_dst.glob("*.ps1"):
        old_ps1.unlink()
        installed.append(f"DEL hooks/{old_ps1.name}")

    (project_root / ".trae" / "logs").mkdir(parents=True, exist_ok=True)
    return installed


# ─── Step 2: V8 残留 → bak_v8doc/ ────────────────────

V8_ONLY_ITEMS = [
    ("docs/CODEMAPS", "dir"),
    ("docs/plans", "dir"),
    ("docs/specs/.buglist", "dir"),       # 如果已拍平到 specs/
    ("docs/specs/changes/.buglist", "dir"),  # 如果在 changes/ 下
    ("docs/specs/.history.md", "file"),
    ("docs/specs/changes/.history.md", "file"),
    ("docs/specs/config.yaml", "file"),
    ("docs/specs/changes/config.yaml", "file"),
    ("docs/.history.md", "file"),
]


def backup_v8_artifacts(project_root: Path, bak_dir: Path, dry_run: bool = False) -> list[str]:
    """将 V8 独有工件移到 bak_v8doc/。"""
    actions = []
    bak_dir.mkdir(parents=True, exist_ok=True)

    for rel_path, kind in V8_ONLY_ITEMS:
        src = project_root / rel_path
        if not src.exists():
            continue

        dst_name = src.name
        dst = bak_dir / dst_name

        # 如果 bak 里已存在同名 → 加时间戳避免覆盖
        if dst.exists():
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            dst = bak_dir / f"{dst_name}.{ts}"

        if dry_run:
            actions.append(f"BAK: {rel_path} → bak_v8doc/{dst.name}")
        else:
            shutil.move(str(src), str(dst))
            actions.append(f"BAK: {rel_path} → bak_v8doc/{dst.name}")

    # 额外: docs/specs/changes/ 下其他 dotfile（非目录）
    changes_dir = project_root / "docs" / "specs" / "changes"
    if changes_dir.exists():
        for item in changes_dir.iterdir():
            if item.name.startswith('.') and item.is_file():
                if dry_run:
                    actions.append(f"BAK: docs/specs/changes/{item.name} → bak_v8doc/{item.name}")
                else:
                    dst = bak_dir / item.name
                    if dst.exists():
                        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
                        dst = bak_dir / f"{item.name}.{ts}"
                    shutil.move(str(item), str(dst))
                    actions.append(f"BAK: docs/specs/changes/{item.name} → bak_v8doc/{dst.name}")

    return actions


# ─── Step 3: 拍平 changes/ → specs/ ──────────────────

V8_SKIP_DIRS = {".buglist", ".history", ".git"}

def flatten_changes_dir(project_root: Path, dry_run: bool = False) -> list[str]:
    """
    V8: docs/specs/changes/{change_name}/
    V9: docs/specs/{change_name}/

    跳过 V8 特有目录（.buglist 等已进入 bak_v8doc/）。
    """
    changes_dir = project_root / "docs" / "specs" / "changes"
    specs_dir = project_root / "docs" / "specs"

    if not changes_dir.exists() or not changes_dir.is_dir():
        return []

    actions = []
    for change_path in sorted(changes_dir.iterdir()):
        if not change_path.is_dir():
            continue
        if change_path.name.startswith('.') or change_path.name in V8_SKIP_DIRS:
            continue

        target = specs_dir / change_path.name
        if target.exists():
            actions.append(f"SKIP changes/{change_path.name}/ (已存在于 specs/)")
            continue
        if dry_run:
            actions.append(f"FLAT: changes/{change_path.name}/ → specs/{change_path.name}/")
        else:
            shutil.move(str(change_path), str(target))
            actions.append(f"FLAT: changes/{change_path.name}/ → specs/{change_path.name}/")

    # 移除空的 changes/ 目录
    if not dry_run and changes_dir.exists():
        remaining = list(changes_dir.iterdir())
        if not remaining:
            changes_dir.rmdir()
            actions.append("RMDIR docs/specs/changes/")
        else:
            actions.append(f"INFO: changes/ 仍有 {len(remaining)} 项残留: {[r.name for r in remaining]}")

    return actions


# ─── Step 4: 转换 state-card ──────────────────────────

def convert_state_card(path: Path, dry_run: bool = False) -> Optional[str]:
    """将 V8 格式的 .state-card.md 转换为 V9.2 格式。"""
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")

    if "V9." in content or "## 变更信息" in content:
        return None

    lines = content.split("\n")
    new_lines = []
    changed = False

    for line in lines:
        orig = line
        line = line.replace("### 基本信息", "## Meta")
        line = line.replace("## 工件进度", "## Artifacts")
        line = line.replace("## 健康度", "## Health")
        line = line.replace("## 下一步", "## Next")
        line = line.replace("## 阻塞", "## Blockers")
        line = line.replace("proposal.md", "define.md")
        line = line.replace("proposal-writer", "definer")
        line = line.replace("fullstack4traev8", "fullstack4traev9")
        line = line.replace("📊", "")
        line = line.replace("🎯", "")
        line = line.replace("🚨", "")
        line = line.replace("docs/specs/changes/", "docs/specs/")

        if "7 维度" in line or "合规性回溯" in line:
            changed = True
            continue

        if orig != line:
            changed = True
        new_lines.append(line)

    if not changed:
        return None

    new_content = "\n".join(new_lines)
    if "V9.2" not in new_content:
        new_content += f"\n\n> Migrated to V9.2 at {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    label = path.parent.name

    if dry_run:
        return f"CONVERT: {label}/.state-card.md"
    else:
        path.write_text(new_content, encoding="utf-8")
        return f"CONVERT: {label}/.state-card.md"


def convert_all_state_cards(project_root: Path, dry_run: bool = False) -> list[str]:
    """转换 specs/ 下所有 state-card（含子目录 + 项目级）。"""
    specs_dir = project_root / "docs" / "specs"
    actions = []

    if not specs_dir.exists():
        return actions

    # 项目级
    root_card = specs_dir / ".state-card.md"
    if root_card.exists():
        result = convert_state_card(root_card, dry_run)
        if result:
            actions.append(result)

    # 子目录级
    for spec_dir in specs_dir.iterdir():
        if not spec_dir.is_dir():
            continue
        if spec_dir.name in ("changes", "archive"):
            continue
        card = spec_dir / ".state-card.md"
        if card.exists():
            result = convert_state_card(card, dry_run)
            if result:
                actions.append(result)

    return actions


# ─── Step 5: Archive 检查 ─────────────────────────────

V8_ARCHIVE_MARKERS = [
    "fullstack4traev8",
    "docs/specs/changes/",
    "📊", "🎯", "🚨",
    "### 基本信息",
    "## 工件进度",
    "## 健康度",
    "📋 下一步",
    "🚨 阻塞",
    "proposal-writer",
    "7 维度",
]


def check_archive(project_root: Path) -> list[str]:
    """检查 archive/done/ 下是否有 V8 格式残留，只报告不修改。"""
    archive_dir = project_root / "docs" / "archive" / "done"
    if not archive_dir.exists():
        return ["INFO: archive/done/ 不存在，跳过"]

    findings = []
    for entry in sorted(archive_dir.iterdir()):
        if not entry.is_dir():
            continue

        v8_hits = []
        for marker in V8_ARCHIVE_MARKERS:
            # 搜索 entry 下所有文件
            for f in entry.rglob("*.md"):
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    if marker in text:
                        rel = f.relative_to(entry)
                        v8_hits.append(f"  {rel}: 含 \"{marker}\"")
                        if len(v8_hits) >= 5:
                            break
                except Exception:
                    pass
            if len(v8_hits) >= 5:
                break

        if v8_hits:
            # 去重
            unique_hits = list(dict.fromkeys(v8_hits))[:5]
            findings.append(f"ARCHIVE {entry.name}: V8 格式残留 ({len(unique_hits)} 处)")
            findings.extend(unique_hits)
        else:
            findings.append(f"ARCHIVE {entry.name}: ✅ 无 V8 格式")

    findings.append("INFO: archive 不可变，以上仅报告不修改。如需清理请手动处理。")
    return findings


# ─── 主流程 ───────────────────────────────────────────

def migrate(project_root: Path, dry_run: bool = False, skip_hooks: bool = False) -> dict:
    """执行完整迁移。"""
    project_root = project_root.resolve()

    if not project_root.exists():
        return {"error": f"项目目录不存在: {project_root}"}

    bak_dir = project_root / "docs" / "bak_v8doc"

    report = {
        "project": str(project_root),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dry_run": dry_run,
        "bak_dir": str(bak_dir),
        "steps": {
            "hooks": [],
            "bak_v8doc": [],
            "flatten": [],
            "state_card": [],
            "archive_check": [],
        },
        "warnings": [],
    }

    # Pre-check
    changes_dir = project_root / "docs" / "specs" / "changes"
    if not changes_dir.exists():
        report["warnings"].append("未发现 docs/specs/changes/ — 可能不是 V8 项目或已迁移")

    # Step 1: Hooks
    if not skip_hooks:
        if dry_run:
            report["steps"]["hooks"] = ["DRY-RUN: 安装 V9.2 hooks (8 .py + hooks.json)"]
        else:
            report["steps"]["hooks"] = install_hooks(project_root)
    else:
        report["steps"]["hooks"] = ["SKIPPED"]

    # Step 2: V8 残留 → bak_v8doc/
    report["steps"]["bak_v8doc"] = backup_v8_artifacts(project_root, bak_dir, dry_run)

    # Step 3: 拍平目录
    report["steps"]["flatten"] = flatten_changes_dir(project_root, dry_run)

    # Step 4: 转换 state-card
    report["steps"]["state_card"] = convert_all_state_cards(project_root, dry_run)

    # Step 5: Archive 检查
    report["steps"]["archive_check"] = check_archive(project_root)

    # 迁移日志
    log_dir = project_root / ".trae" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"migrate-v8-to-v9-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    log_entries = [f"[{report['timestamp']}] V8→V9.2 Migration {'(DRY-RUN)' if dry_run else ''}"]
    for step_name, items in report["steps"].items():
        if items:
            log_entries.extend(f"  [{step_name}] {item}" for item in items)
    if not dry_run:
        log_file.write_text("\n".join(log_entries), encoding="utf-8")
    report["log_file"] = str(log_file)

    return report


# ─── CLI ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="V8 → V9.2 项目迁移")
    parser.add_argument("--project-root", required=True, help="目标项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际执行")
    parser.add_argument("--skip-hooks", action="store_true", help="跳过 hooks 安装")
    args = parser.parse_args()

    report = migrate(
        Path(args.project_root),
        dry_run=args.dry_run,
        skip_hooks=args.skip_hooks,
    )

    print(f"V8 → V9.2 迁移 {'(DRY-RUN)' if args.dry_run else ''}")
    print(f"项目: {report['project']}")
    print(f"V8 残留 → {report['bak_dir']}")
    print()

    for step_name, items in report["steps"].items():
        if items:
            label = {
                "hooks": "Step 1 — Hooks 升级",
                "bak_v8doc": "Step 2 — V8 残留 → bak_v8doc/",
                "flatten": "Step 3 — 拍平 changes/ → specs/",
                "state_card": "Step 4 — state-card 转换",
                "archive_check": "Step 5 — Archive 检查",
            }.get(step_name, step_name)
            print(f"## {label}")
            for item in items:
                print(f"  {item}")
            print()

    if report["warnings"]:
        print("## Warnings")
        for w in report["warnings"]:
            print(f"  ⚠️ {w}")
        print()

    if not args.dry_run:
        print(f"迁移日志: {report.get('log_file', 'N/A')}")
        print()
        print("下一步:")
        print("  1. 重启 IDE 使新 hooks 生效")
        print("  2. python scripts/change-status.py docs/specs/ -- 验证状态")
        print("  3. 继续 V9.2 工作流")

    if "error" in report:
        print(f"❌ {report['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
