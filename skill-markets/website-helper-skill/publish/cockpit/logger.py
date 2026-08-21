"""Cockpit state card updater — sync publish history to docs/specs/.state-card.md."""

import os
import time
from datetime import datetime, timezone
from typing import Optional

from publish.models import PublishRecord, PublishOperation, PublishStatus

# We reference the project root relative to this file.
# The state card lives at docs/specs/.state-card.md relative to project root.
# Since CLI is invoked from project root, use cwd.

STATE_CARD_PATH = "docs/specs/.state-card.md"
HISTORY_HEADER = "## 发布历史"


def _get_project_root() -> str:
    """Get project root from current working directory."""
    return os.getcwd()


def _timestamp() -> str:
    """Get current ISO 8601 timestamp."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_state_card() -> list[str]:
    """Read state card lines. Returns empty list if file doesn't exist."""
    path = os.path.join(_get_project_root(), STATE_CARD_PATH)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


def _write_state_card(lines: list[str]) -> None:
    """Write state card lines back to file."""
    path = os.path.join(_get_project_root(), STATE_CARD_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(lines)


def log_publish(
    subdomain: str,
    operation: PublishOperation,
    status: PublishStatus,
    detail: str = "",
) -> PublishRecord:
    """Log a publish operation to the cockpit state card."""
    record = PublishRecord(
        timestamp=_timestamp(),
        subdomain=subdomain,
        operation=operation,
        status=status,
        detail=detail,
    )

    lines = _read_state_card()

    # Find or create ## 发布历史 section
    history_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith(HISTORY_HEADER):
            history_idx = i
            break

    if history_idx is None:
        # Append history section at end
        if lines and lines[-1].strip() != "":
            lines.append("\n")
        lines.append(f"\n{HISTORY_HEADER}\n\n")
        history_idx = len(lines) - 2  # The header line

    # Find the table header row (starts with | timestamp)
    table_start = None
    for i in range(history_idx + 1, len(lines)):
        if lines[i].strip().startswith("| 时间戳"):
            table_start = i
            break

    if table_start is None:
        # Create table header
        header = "| 时间戳 | 子域名 | 操作 | 结果 |\n"
        sep = "|--------|--------|------|------|\n"
        lines.insert(history_idx + 2, header)
        lines.insert(history_idx + 3, sep)
        table_start = history_idx + 2

    # Insert record after header+sep (before any existing records, newest first)
    insert_at = table_start + 2
    row = f"| {record.timestamp} | {subdomain} | {operation.value} | {record.to_markdown_row().split('|')[-2].strip()} |\n"
    lines.insert(insert_at, row)

    _write_state_card(lines)
    return record


def list_published() -> list[PublishRecord]:
    """List all published domains from state card."""
    lines = _read_state_card()
    records = []

    in_history = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(HISTORY_HEADER):
            in_history = True
            continue
        if in_history and stripped.startswith("##"):
            break  # next section, stop
        if in_history and stripped.startswith("|"):
            parts = [p.strip() for p in stripped.split("|") if p.strip()]
            if len(parts) >= 4 and parts[0] != "时间戳":
                try:
                    records.append(PublishRecord(
                        timestamp=parts[0],
                        subdomain=parts[1],
                        operation=PublishOperation(parts[2]),
                        status=PublishStatus(parts[3].replace("✅ ", "").replace("⚠️ ", "").replace("❌ ", "")),
                    ))
                except (ValueError, IndexError):
                    pass  # skip malformed lines

    return records


def get_latest_record(subdomain: str) -> Optional[PublishRecord]:
    """Get latest publish record for a subdomain."""
    all_records = list_published()
    for r in all_records:
        if r.subdomain == subdomain:
            return r
    return None
