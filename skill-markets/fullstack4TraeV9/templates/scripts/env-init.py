"""V9 Project Environment Init/Check Script (Python)

Usage: python env-init.py [--project-root <path>] [--fix] [--verbose]
  --fix: auto-create missing dirs/files from templates
  --verbose: show detailed paths
Output: environment check report + suggestions
Principle: run after each skill upgrade to ensure project environment is complete
"""

import argparse
import shutil
import os
from pathlib import Path
from datetime import datetime


SKILL_TEMPLATES = Path.home() / ".trae-cn" / "skills" / "fullstack4traev9" / "templates"

ITEMS = [
    # (label, relative_path, type)
    # type: "dir" | "file" | "hook"
    ("docs/specs/", "docs/specs", "dir"),
    ("docs/modules/", "docs/modules", "dir"),
    ("docs/prototypes/ (V9 project-level)", "docs/prototypes", "dir"),
    ("docs/test-plan/ (V9 test plan)", "docs/test-plan", "dir"),
    ("docs/CODEMAPS/", "docs/CODEMAPS", "dir"),
    ("docs/contracts/ (project-level)", "docs/contracts", "dir"),
    ("docs/archive/out/ (V9 obsoleted)", "docs/archive/out", "dir"),
    ("docs/archive/done/ (V9 completed)", "docs/archive/done", "dir"),
    ("docs/specs/config.yaml", "docs/specs/config.yaml", "file"),
    ("docs/specs/.state-card.md (V9 Cockpit)", "docs/specs/.state-card.md", "file"),
    (".trae/hooks.json", ".trae/hooks.json", "file"),
    ("scripts/debug/", "scripts/debug", "dir"),
    ("llm-prompts/ (V9 prompt snapshots)", "llm-prompts", "dir"),
]

HOOK_SCRIPTS = [
    "session-start.ps1",
    "complexity-guard.ps1",
    "doc-sync-gate.ps1",
    "contract-gate.ps1",
    "spec-validate-hook.ps1",
    "auto-test.ps1",
    "drift-detect.ps1",
    "tasks-integrity.ps1",
]

CORE_SCRIPTS = [
    "render-cockpit.py",
    "log-agent-prompt.py",
    "env-init.py",
]

# Map item label -> (template source subpath, is_optional)
TEMPLATE_MAP = {
    "docs/specs/config.yaml": ("config.yaml", False),
    "docs/specs/.state-card.md (V9 Cockpit)": ("cockpit-state-card.md", False),
    ".trae/hooks.json": ("hooks/fullstack-hooks.json", False),
}


def check(project_root: Path) -> list[dict]:
    """Check all items and return results."""
    results = []
    for label, rel_path, item_type in ITEMS:
        full_path = project_root / rel_path
        exists = full_path.exists()
        results.append({
            "label": label,
            "path": full_path,
            "type": item_type,
            "exists": exists,
        })

    # Hook scripts
    hooks_dir = project_root / ".trae" / "hooks"
    for hs in HOOK_SCRIPTS:
        fp = hooks_dir / hs
        results.append({
            "label": f".trae/hooks/{hs}",
            "path": fp,
            "type": "file",
            "exists": fp.exists(),
        })

    # Core scripts
    for cs in CORE_SCRIPTS:
        fp = hooks_dir / cs
        results.append({
            "label": f".trae/hooks/{cs}",
            "path": fp,
            "type": "file",
            "exists": fp.exists(),
        })

    return results


def fix(project_root: Path, missing: list[dict]) -> list[str]:
    """Auto-create missing items. Returns list of created labels."""
    created = []

    for item in missing:
        path = item["path"]
        label = item["label"]
        item_type = item["type"]

        try:
            if item_type == "dir":
                path.mkdir(parents=True, exist_ok=True)
                created.append(label)

            elif item_type == "file":
                path.parent.mkdir(parents=True, exist_ok=True)

                # Try template copy
                copied = False
                if label in TEMPLATE_MAP:
                    template_rel, _ = TEMPLATE_MAP[label]
                    template_path = SKILL_TEMPLATES / template_rel
                    if template_path.exists():
                        shutil.copy2(template_path, path)
                        copied = True

                if not copied and label.startswith(".trae/hooks/"):
                    script_name = label.split("/")[-1]
                    # Try hooks dir first, then scripts dir
                    for subdir in ("hooks", "scripts"):
                        template_path = SKILL_TEMPLATES / subdir / script_name
                        if template_path.exists():
                            shutil.copy2(template_path, path)
                            copied = True
                            break

                if not copied:
                    path.touch()

                created.append(label)

        except Exception as e:
            print(f"  [FAIL] {label}: {e}")

    return created


def main():
    parser = argparse.ArgumentParser(description="V9 Environment Init/Check")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--fix", action="store_true", help="Auto-create missing items")
    parser.add_argument("--verbose", action="store_true", help="Show detailed paths")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    results = check(project_root)

    total = len(results)
    ok = sum(1 for r in results if r["exists"])
    missing = [r for r in results if not r["exists"]]

    print("")
    print("# V9 Environment Check Report")
    print("")
    print(f"Project: {project_root.name}")
    print(f"Path: {project_root}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    print(f"## Result: {ok} / {total} ready")
    print("")

    for r in results:
        icon = "[OK]" if r["exists"] else "[MISS]"
        line = f"{icon} {r['label']}"
        if args.verbose:
            line += f" -- {r['path']}"
        print(line)
    print("")

    if missing:
        print("## Missing Items")
        print("")
        for m in missing:
            print(f"- [{m['type']}] {m['label']}")
        print("")

        if args.fix:
            print("## Auto-Fixing")
            print("")
            created = fix(project_root, missing)
            for label in created:
                print(f"  [FIXED] {label}")
            print("")
            print(f"Fixed {len(created)} missing items. Re-run check to confirm.")
            print("")
        else:
            print("## Fix Suggestions")
            print("")
            print("Run with --fix to auto-complete:")
            print("")
            print("```")
            print("python .trae/hooks/env-init.py --fix")
            print("```")
            print("")
            missing_hooks = [m for m in missing if '.ps1' in m['label'] or 'hooks.json' in m['label']]
            if missing_hooks:
                print("For hook installation, use the canonical installer:")
                print("")
                print("```")
                print("python ~/.trae-cn/skills/fullstack4TraeV9/scripts/install-hooks.py --project-root .")
                print("```")
                print("")
    else:
        print("[OK] All items ready. V9 environment is complete.")
        print("")

    print("---")
    print("*Check script: templates/scripts/env-init.py*")
    print("")


if __name__ == "__main__":
    main()
