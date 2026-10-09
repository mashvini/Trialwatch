"""Lawyer decisions: an append-only audit log per case (data/<case>/audit_log.jsonl)."""
from __future__ import annotations

from pathlib import Path

from .schemas import Decision, Flag

AUDIT_FILE = "audit_log.jsonl"


def record_decision(case_dir: Path, decision: Decision) -> None:
    """Append one decision. The log is never rewritten, so the history is preserved."""
    path = Path(case_dir) / AUDIT_FILE
    with path.open("a", encoding="utf-8") as f:
        f.write(decision.model_dump_json() + "\n")


def load_decisions(case_dir: Path) -> list[Decision]:
    path = Path(case_dir) / AUDIT_FILE
    if not path.exists():
        return []
    return [Decision.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def apply_decisions(flags: list[Flag], decisions: list[Decision]) -> None:
    """Set each flag's status from its latest decision (in place)."""
    latest = {d.flag_id: d.decision for d in decisions}  # later lines overwrite earlier ones
    for flag in flags:
        if flag.id in latest:
            flag.status = latest[flag.id]
