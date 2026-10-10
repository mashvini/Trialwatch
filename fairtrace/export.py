"""Draft findings for accepted potential issues, as Markdown."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from . import redact
from .schemas import CaseRecord, Flag
from .taxonomy import Right


def export_markdown(
    record: CaseRecord, rights: list[Right], reviewer: str = "", restore_names: dict[str, str] | None = None
) -> str:
    """T9. Build the draft findings document.

    Spec (tests/test_spec_export.py):
    - Title: "# Draft findings: <case title>"
    - A note under the title: an AI-assisted draft, reviewed by <reviewer>; potential issues only;
      the legal assessment and any grade remain the expert's. Mention "SYNTHETIC DATA" if case.synthetic,
      and the case's provenance (where reconstructed material comes from) if it has one.
    - One "## <right name>" section per right (in rights.yaml order) that has ACCEPTED flags.
      Pending, rejected and needs_facts flags never appear in these sections.
    - Each accepted flag: its explanation, followed by footnote markers [^n] for its source lines.
      If a Devil's Advocate challenge exists: "State's likely response: <argument> (record check: <verdict>)".
    - Footnotes at the end: "[^n]: <source id>: <line text>" for every cited line.
    - A final "## Open questions for the monitor" section listing missing_facts of accepted and
      needs_facts flags, grouped by hearing.
    - restore_names (T11): if the lawyer chooses, the names.yaml map; "[ROLE]" becomes the real name.
    """
    case = record.case
    lines = record.lines_by_id()
    challenges = {c.flag_id: c for c in record.challenges}
    accepted = [f for f in record.flags if f.status == "accepted"]
    footnotes: dict[str, int] = {}  # source id -> footnote number; a line cited twice keeps one note

    out = [f"# Draft findings: {case.title}", ""]
    if case.synthetic:
        out += ["> **SYNTHETIC DATA**: invented for testing. Not a real case.", ""]
    if case.provenance:
        out += [f"> **SOURCE**: {case.provenance}", ""]
    out += [
        f"> AI-assisted draft, reviewed by {reviewer or '(no reviewer named)'}. It lists potential issues only; "
        "the legal assessment and any grade remain the expert's.",
        "",
    ]

    if not accepted:
        out += ["No potential issues have been accepted yet.", ""]
    for right in rights:
        flags = [f for f in accepted if f.right_id == right.id]
        if not flags:
            continue
        out += [f"## {right.name}", ""]
        for f in flags:
            marks = "".join(f"[^{footnotes.setdefault(sid, len(footnotes) + 1)}]" for sid in f.source_ids)
            out += [f"{f.explanation}{marks}", ""]
            challenge = challenges.get(f.id)
            if challenge:
                verdict = challenge.verdict.replace("_", " ")
                out += [f"*State's likely response:* {challenge.state_argument} (record check: {verdict})", ""]

    out += ["## Open questions for the monitor", ""]
    questions = monitor_questions(record, ("accepted", "needs_facts"))
    if not questions:
        out += ["None.", ""]
    for group, items in questions.items():
        out += [f"**{group}**", ""] + [f"- {item.question}" for item in items] + [""]

    for sid, n in footnotes.items():
        text = lines[sid].text if sid in lines else "(source line not found)"
        out.append(f"[^{n}]: {sid}: {text}")
    md = "\n".join(out).rstrip() + "\n"
    return redact.restore(md, restore_names) if restore_names else md


class MonitorQuestion(BaseModel):
    """One follow-up question for the trial monitor, and where it came from."""

    question: str
    flag_id: str
    source: Literal["missing_fact", "devils_advocate"]


def monitor_questions(
    record: CaseRecord, statuses: tuple[str, ...], include_challenges: bool = False
) -> dict[str, list[MonitorQuestion]]:
    """Questions for the monitor, grouped by the hearing of each flag's first source (Gap Finder).

    Sources: missing_facts of flags whose status is in `statuses`, and, if include_challenges,
    every "not_addressed" Devil's Advocate challenge (the record is silent, so ask). Groups follow
    the case's hearing order, then documents; a question asked twice in a group appears once.
    """
    challenges = {c.flag_id: c for c in record.challenges}
    groups: dict[str, list[MonitorQuestion]] = {_group_label(record, h.id): [] for h in record.case.hearings}
    for f in record.flags:
        if f.status not in statuses:
            continue
        items = [MonitorQuestion(question=q, flag_id=f.id, source="missing_fact") for q in f.missing_facts]
        challenge = challenges.get(f.id)
        if include_challenges and challenge and challenge.verdict == "not_addressed":
            items.append(
                MonitorQuestion(
                    question=f"The record is silent on a possible justification: {challenge.state_argument} "
                    "Did anything at the hearing bear on this?",
                    flag_id=f.id,
                    source="devils_advocate",
                )
            )
        group = groups.setdefault(_group_label(record, _first_doc(record, f)), [])
        group += [item for item in items if item.question not in {g.question for g in group}]
    return {label: items for label, items in groups.items() if items}


def questions_checklist(record: CaseRecord, groups: dict[str, list[MonitorQuestion]]) -> str:
    """The monitor's questions as a Markdown checklist they can fill in while the hearing is fresh."""
    out = [f"# Questions for the monitor: {record.case.title}", ""]
    if record.case.synthetic:
        out += ["> **SYNTHETIC DATA**: invented for testing. Not a real case.", ""]
    if record.case.provenance:
        out += [f"> **SOURCE**: {record.case.provenance}", ""]
    out += ["Facts the notes do not record. Please answer what you saw or heard; leave blank if unsure.", ""]
    if not groups:
        out += ["No open questions.", ""]
    for label, items in groups.items():
        out += [f"## {label}", ""]
        out += [f"- [ ] {item.question} *(potential issue `{item.flag_id}`)*" for item in items]
        out += [""]
    return "\n".join(out).rstrip() + "\n"


def _first_doc(record: CaseRecord, flag: Flag) -> str:
    """The hearing or document id of the flag's first cited line ("?" if it has none)."""
    by_id = record.lines_by_id()
    return by_id[flag.source_ids[0]].doc if flag.source_ids and flag.source_ids[0] in by_id else "?"


def _group_label(record: CaseRecord, doc: str) -> str:
    hearing = next((h for h in record.case.hearings if h.id == doc), None)
    if hearing is None:
        return f"Documents ({doc})"
    return f"Hearing {doc}" + (f" ({hearing.date})" if hearing.date else "")
