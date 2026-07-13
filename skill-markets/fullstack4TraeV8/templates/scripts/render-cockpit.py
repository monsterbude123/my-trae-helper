"""V7 Cockpit Rendering Script (Python)

Usage: python render-cockpit.py [--project-root <path>] [--change <name>]
Output: formatted Cockpit Markdown (LLM displays directly, does NOT generate)
Principle: Cockpit rendered by script, not LLM -- ensures format consistency
"""

import argparse
import re
import os
from datetime import datetime
from pathlib import Path


def parse_state_card(path: Path) -> dict | None:
    """Parse a per-change .state-card.md file."""
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    card = {}

    STAGE_NAMES = {
        'intake', 'proposal', 'specs', 'spec', 'roundtable',
        'contract', 'design', 'dev', 'review', 'accept'
    }

    # Collect all **field**: value pairs in order (may be in list items)
    fields = []
    for line in content.splitlines():
        m = re.match(r'^(?:\s*-\s*)?\*\*([^*]+)\*\*:\s*(.+)$', line.strip())
        if m:
            fields.append((m.group(1).strip(), m.group(2).strip()))

    # Positional field identification
    # Order: change, stage(N/8), stage_name, last_output, active_agent, prompt_path
    for idx, (fname, fval) in enumerate(fields):
        # Stage line: value like "3 / 8"
        if re.match(r'\d+\s*/\s*\d+$', fval):
            sm = re.match(r'(\d+)\s*/\s*\d+', fval)
            card['stage'] = int(sm.group(1))
            # Next field is typically stage_name
            if idx + 1 < len(fields):
                next_val = fields[idx + 1][1].strip()
                if next_val.lower() in STAGE_NAMES:
                    card['stage_name'] = next_val
            continue

        # Stage name on its own
        if fval.strip().lower() in STAGE_NAMES:
            card.setdefault('stage_name', fval.strip())
            continue

        # Timestamp: YYYY-MM-DD HH:MM
        if re.match(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}', fval):
            card['last_output'] = fval
            continue

        # Agent name: matches known agent patterns
        if re.match(r'^[a-z]+[-]?[a-z]*$', fval, re.IGNORECASE) and len(fval) > 3:
            card['active_agent'] = fval
            continue

        # Prompt path: looks like a file path (contains "/" and ends with .md)
        if '/' in fval and fval.endswith('.md'):
            card['prompt_path'] = fval
            continue

        # Change name: first field, often has hyphens
        if idx == 0:
            card['change'] = fval
            continue

    # Parse **field**: value lines for health info (inside any section)
    # Health fields come in fixed order: spec_drift, contract_drift, alignment
    health_values = []
    for line in content.splitlines():
        m = re.match(r'^(?:\s*-\s*)?\*\*([^*]+)\*\*:\s*(.+)$', line.strip())
        if not m:
            continue
        field_name = m.group(1).strip()
        field_value = m.group(2).strip()

        # Position-based health parsing: first 3 health-related fields
        # Health section fields are: drift fields + alignment
        # Skip non-health fields (stage/changes etc. already handled above)
        if health_values:
            # Already started collecting, continue
            if re.search(r'[Aa]lign', field_name) or re.match(r'\d+%', field_value):
                health_values.append(field_value)
                break  # alignment is last
            else:
                health_values.append(field_value)
        else:
            # Check if this looks like a health field (emojis ✅❌⚠️ or percentage)
            if re.search(r'[✅❌⚠️🟢🟡🔴]', field_value) or re.match(r'\d+%', field_value):
                health_values.append(field_value)
    
    if len(health_values) >= 1:
        card['spec_drift'] = health_values[0]
    if len(health_values) >= 2:
        card['contract_drift'] = health_values[1]
    if len(health_values) >= 3:
        # alignment: extract percentage
        m2 = re.search(r'(\d+)%', health_values[2])
        if m2:
            card['alignment'] = int(m2.group(1))

    # Parse sections: Next Step and Blocker (last two sections)
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    # The last two sections are typically "next_step" and "blocker"
    step_sections = []
    for section in sections[1:]:  # skip content before first ##
        m = re.match(r'(.+?)\s*\n-\s*(.+?)(?:\n|$)', section, re.DOTALL)
        if m:
            step_sections.append((m.group(1).strip(), m.group(2).strip()))

    # Last two sections: penultimate = next_step, last = blocker
    if len(step_sections) >= 2:
        card['next_step'] = step_sections[-2][1]
        card['blocker'] = step_sections[-1][1]
    elif len(step_sections) >= 1:
        card['next_step'] = step_sections[-1][1]

    # Parse artifact table
    card['artifacts'] = {}
    for m in re.finditer(r'\|\s*(\S+(?:\.(?:md|ts|js|json|yaml|yml)|/)?\S*)\s*\|\s*(\S+)\s*\|\s*(.+?)\s*\|', content):
        name = m.group(1).strip()
        status = m.group(2).strip()
        apath = m.group(3).strip()
        card['artifacts'][name] = {'status': status, 'path': apath}

    return card


def parse_project_cockpit(path: Path) -> dict | None:
    """Parse project-level .state-card.md."""
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    cockpit = {'changes': [], 'health': {}, 'artifacts': {}}

    # Parse active changes table (7-col new format first, then 6-col old)
    for m in re.finditer(
        r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|',
        content
    ):
        cockpit['changes'].append({
            'number': m.group(1).strip(),
            'name': m.group(2).strip(),
            'stage': m.group(3).strip(),
            'agent': m.group(4).strip(),
            'status': m.group(5).strip(),
            'last_activity': m.group(6).strip(),
            'blocker': m.group(7).strip(),
        })

    if not cockpit['changes']:
        for m in re.finditer(
            r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|',
            content
        ):
            cockpit['changes'].append({
                'number': m.group(1).strip(),
                'name': m.group(2).strip(),
                'stage': m.group(3).strip(),
                'agent': '',
                'status': m.group(4).strip(),
                'last_activity': m.group(5).strip(),
                'blocker': m.group(6).strip(),
            })

    # Health overview: match **...**: value lines
    health_matches = list(re.finditer(r'\*\*[^*]+\*\*:\s*(.+)', content))
    if len(health_matches) >= 1 and re.match(r'^\d+$', health_matches[0].group(1).strip()):
        cockpit['health']['active_changes'] = int(health_matches[0].group(1).strip())
    if len(health_matches) >= 2 and re.match(r'^\d+$', health_matches[1].group(1).strip()):
        cockpit['health']['blocked_changes'] = int(health_matches[1].group(1).strip())
    if len(health_matches) >= 3:
        cockpit['health']['spec_risk'] = health_matches[2].group(1).strip()

    # Project-level artifacts
    artifact_section = False
    for line in content.splitlines():
        if re.match(r'^## .*[Aa]rtifacts.*', line):
            artifact_section = True
            continue
        if artifact_section and re.match(r'^## ', line):
            break
        if artifact_section:
            m = re.match(r'-\s*(.+?):\s*(.+)', line)
            if m:
                cockpit['artifacts'][m.group(1).strip()] = m.group(2).strip()

    return cockpit


def get_agent_history(llm_prompts_dir: Path) -> list:
    """Scan llm-prompts/ for agent call history."""
    history = []
    if not llm_prompts_dir.exists():
        return history

    index_file = llm_prompts_dir / "INDEX.md"
    if index_file.exists():
        content = index_file.read_text(encoding="utf-8")
        for m in re.finditer(r'\|\s*(\d{4}[-]\d{2}[-]\d{2}[-]\d{6})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', content):
            history.append({
                'timestamp': m.group(1).strip(),
                'agent': m.group(2).strip(),
                'path': m.group(3).strip(),
                'change': m.group(4).strip(),
            })
    else:
        for f in sorted(llm_prompts_dir.glob("*.md"), key=os.path.getmtime, reverse=True):
            history.append({
                'timestamp': datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M'),
                'agent': re.sub(r'^\d{4}-\d{2}-\d{2}-\d{6}-', '', f.stem),
                'path': f"llm-prompts/{f.name}",
                'change': '',
            })

    return history


PIPELINE_STAGES = [
    ("cockpit",    "Cockpit",    "Main Agent"),
    ("intake",     "Intake",     "intake"),
    ("proposal",   "Proposal",   "proposal-writer"),
    ("specs",      "Spec",       "spec-writer"),
    ("roundtable", "Roundtable", "Main Agent (host)"),
    ("contract",   "Contract",   "contract-writer"),
    ("design",     "Design",     "planner"),
    ("dev",        "Dev",        "implementer"),
    ("review",     "Review",     "reviewer"),
    ("accept",     "Accept",     "acceptance-discipline"),
]


def render(project_root: Path, change: str | None = None) -> str:
    """Render the full cockpit Markdown."""
    lines = []
    w = lines.append

    specs_dir = project_root / "docs" / "specs"
    changes_dir = specs_dir / "changes"
    cockpit_file = specs_dir / ".state-card.md"
    llm_prompts_dir = project_root / "llm-prompts"

    cockpit = parse_project_cockpit(cockpit_file)

    w("")
    w("# V7 Cockpit")
    w("")

    # Active changes table
    if cockpit and cockpit['changes']:
        w("## Active Changes")
        w("")
        w("| # | Change | Stage | Agent | Status | Last Activity | Blocker |")
        w("|---|--------|-------|-------|--------|--------------|---------|")
        for c in cockpit['changes']:
            w(f"| {c['number']} | {c['name']} | {c['stage']} | {c['agent']} | {c['status']} | {c['last_activity']} | {c['blocker']} |")
        w("")
        w("## Health")
        active = cockpit['health'].get('active_changes', '?')
        blocked = cockpit['health'].get('blocked_changes', '?')
        risk = cockpit['health'].get('spec_risk', '?')
        w(f"- **Active**: {active} | **Blocked**: {blocked} | **Spec risk**: {risk}")
        w("")

    # Pipeline progress
    w("## Pipeline")
    w("")
    active_stages = {c['stage']: c['name'] for c in cockpit['changes']} if cockpit else {}

    pipe_line = ""
    pipe_line2 = ""
    for code, label, _agent in PIPELINE_STAGES:
        if code in active_stages:
            pipe_line += f"**[``{label}``]** -> "
            pipe_line2 += f"   {active_stages[code]}    "
        else:
            pipe_line += f"``{label}`` -> "
            pipe_line2 += " " * (len(label) + 10)
    w(pipe_line[:-4])
    w(pipe_line2.rstrip())
    w("")

    # Per-change details
    if change:
        change_dir = changes_dir / change
        card = parse_state_card(change_dir / ".state-card.md")
        if card:
            w(f"## Change: {change}")
            w("")
            w("| Field | Value |")
            w("|-------|-------|")
            stage_name = card.get('stage_name', '?')
            stage = card.get('stage', '?')
            w(f"| Stage | {stage_name} ({stage}/9) |")
            w(f"| Last Output | {card.get('last_output', '?')} |")
            if card.get('active_agent'):
                w(f"| Active Agent | {card['active_agent']} |")
            if card.get('prompt_path'):
                w(f"| Prompt Path | {card['prompt_path']} |")
            w(f"| Next Step | {card.get('next_step', '?')} |")
            w(f"| Blocker | {card.get('blocker', '?')} |")
            w("")

            w("### Artifacts")
            w("| Artifact | Status | Path |")
            w("|----------|--------|------|")
            for name, a in card.get('artifacts', {}).items():
                w(f"| {name} | {a['status']} | {a['path']} |")
            w("")

            align = card.get('alignment', 0)
            emoji = "HIGH" if align >= 90 else "MED" if align >= 70 else "LOW"
            w("### Health")
            w(f"- Spec Drift: {card.get('spec_drift', '?')}")
            w(f"- Contract Drift: {card.get('contract_drift', '?')}")
            w(f"- Alignment: {emoji} {align}%")
            w("")

    elif cockpit and cockpit['changes']:
        for c in cockpit['changes']:
            card = parse_state_card(changes_dir / c['name'] / ".state-card.md")
            if not card:
                continue
            w(f"## {c['name']} ({c['status']})")
            w("| Field | Value |")
            w("|-------|-------|")
            stage_name = card.get('stage_name', '?')
            stage = card.get('stage', '?')
            w(f"| Stage | {stage_name} ({stage}/9) |")
            w(f"| Last Output | {card.get('last_output', '?')} |")
            if card.get('active_agent'):
                w(f"| Active Agent | {card['active_agent']} |")
            if card.get('prompt_path'):
                w(f"| Prompt Path | {card['prompt_path']} |")
            w(f"| Next Step | {card.get('next_step', '?')} |")
            w(f"| Blocker | {card.get('blocker', '?')} |")
            w("")

            # Active file references
            active_files = [
                (name, a) for name, a in card.get('artifacts', {}).items()
                if a['status'] in ('⏳', '✅') and a['path'] != '-'
            ]
            if active_files:
                w("### Active Files")
                w("| Artifact | Path | Status |")
                w("|----------|------|--------|")
                for name, a in active_files:
                    w(f"| {name} | {a['path']} | {a['status']} |")
                w("")

            align = card.get('alignment', 0)
            emoji = "HIGH" if align >= 90 else "MED" if align >= 70 else "LOW"
            w("### Health")
            w(f"- Spec Drift: {card.get('spec_drift', '?')}")
            w(f"- Contract Drift: {card.get('contract_drift', '?')}")
            w(f"- Alignment: {emoji} {align}%")
            w("")

    # Agent call history
    agent_history = get_agent_history(llm_prompts_dir)
    if agent_history:
        w("## Recent Agent Calls")
        w("| Time | Agent | Prompt File | Change |")
        w("|------|-------|-------------|--------|")
        for entry in agent_history[:10]:
            w(f"| {entry['timestamp']} | {entry['agent']} | {entry['path']} | {entry['change']} |")
        w("")

    # Project-level artifacts
    if cockpit and cockpit['artifacts']:
        w("## Project Artifacts")
        for key, val in cockpit['artifacts'].items():
            w(f"- {key}: {val}")
        w("")

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    w("---")
    w(f"*Rendered: {now} | script: templates/scripts/render-cockpit.py*")
    w("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="V7 Cockpit Renderer")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--change", default=None, help="Filter to single change")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    output = render(project_root, args.change)
    print(output)


if __name__ == "__main__":
    main()
