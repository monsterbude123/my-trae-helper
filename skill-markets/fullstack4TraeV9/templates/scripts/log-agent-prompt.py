"""V9 Agent Prompt Logging Script (Python)

Usage: python log-agent-prompt.py --agent-name "spec-writer" --prompt "content" [--change "name"] [--project-root <path>]
Output: ./llm-prompts/{timestamp}-{agent-name}.md + update INDEX.md
Purpose: reference what prompt an agent received on re-entry
"""

import argparse
from datetime import datetime
from pathlib import Path


def log_prompt(project_root: Path, agent_name: str, prompt: str, change: str = ""):
    prompts_dir = project_root / "llm-prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    fname = f"{timestamp}-{agent_name}.md"
    fpath = prompts_dir / fname

    # Write prompt snapshot
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    change_label = change if change else "--"
    project_label = project_root.name

    fpath.write_text(
        f"# Agent Prompt Snapshot\n\n"
        f"- **Agent**: {agent_name}\n"
        f"- **Time**: {now}\n"
        f"- **Change**: {change_label}\n"
        f"- **Project**: {project_label}\n\n"
        f"---\n\n"
        f"{prompt}\n",
        encoding="utf-8"
    )

    # Update INDEX.md
    index_file = prompts_dir / "INDEX.md"
    entry = f"| {timestamp} | {agent_name} | llm-prompts/{fname} | {change_label} |"

    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        import re
        m = re.search(r'(\|\s*Time\s*\|.*\|.*\|.*\|)', content)
        if m:
            new_content = content.replace(m.group(1), f"{m.group(1)}\n{entry}")
            index_file.write_text(new_content, encoding="utf-8")
        else:
            _create_index(index_file, entry)
    else:
        _create_index(index_file, entry)

    print(f"OK: {fpath}")
    print(f"OK: {index_file} (updated)")


def _create_index(index_file: Path, entry: str):
    index_file.write_text(
        "# llm-prompts Index\n\n"
        "> Agent prompt snapshots. Auto-recorded when sub-agents start, for re-entry reference.\n\n"
        "| Time | Agent | File | Change |\n"
        "|------|-------|------|--------|\n"
        f"{entry}\n",
        encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description="V9 Agent Prompt Logger")
    parser.add_argument("--agent-name", required=True, help="Agent name (e.g. spec-writer)")
    parser.add_argument("--prompt", required=True, help="Prompt content to log")
    parser.add_argument("--change", default="", help="Associated change name")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    args = parser.parse_args()

    log_prompt(Path(args.project_root).resolve(), args.agent_name, args.prompt, args.change)


if __name__ == "__main__":
    main()
