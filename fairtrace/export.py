"""Draft findings for accepted potential issues, as Markdown."""
from __future__ import annotations

from .schemas import CaseRecord
from .taxonomy import Right


def export_markdown(record: CaseRecord, rights: list[Right], reviewer: str = "") -> str:
    """T9. Build the draft findings document.

    Spec (tests/test_spec_export.py):
    - Title: "# Draft findings: <case title>"
    - A note under the title: an AI-assisted draft, reviewed by <reviewer>; potential issues only;
      the legal assessment and any grade remain the expert's. Mention "SYNTHETIC DATA" if case.synthetic.
    - One "## <right name>" section per right (in rights.yaml order) that has ACCEPTED flags.
      Pending, rejected and needs_facts flags never appear in these sections.
    - Each accepted flag: its explanation, followed by footnote markers [^n] for its source lines.
      If a Devil's Advocate challenge exists: "State's likely response: <argument> (record check: <verdict>)".
    - Footnotes at the end: "[^n]: <source id>: <line text>" for every cited line.
    - A final "## Open questions for the monitor" section listing missing_facts of accepted and
      needs_facts flags, grouped by hearing.
    """
    case = record.case
    lines = record.lines_by_id()
    challenges = {c.flag_id: c for c in record.challenges}
    accepted = [f for f in record.flags if f.status == "accepted"]
    footnotes: dict[str, int] = {}  # source id -> footnote number; a line cited twice keeps one note

    out = [f"# Draft findings: {case.title}", ""]
    if case.synthetic:
        out += ["> **SYNTHETIC DATA**: invented for testing. Not a real case.", ""]
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
    questions = _open_questions(record)
    if not questions:
        out += ["None.", ""]
    for group, items in questions.items():
        out += [f"**{group}**", ""] + [f"- {q}" for q in items] + [""]

    for sid, n in footnotes.items():
        text = lines[sid].text if sid in lines else "(source line not found)"
        out.append(f"[^{n}]: {sid}: {text}")
    return "\n".join(out).rstrip() + "\n"


def _open_questions(record: CaseRecord) -> dict[str, list[str]]:
    """missing_facts of accepted and needs_facts flags, grouped by the hearing of their first source."""
    hearing_ids = {h.id for h in record.case.hearings}
    by_id = record.lines_by_id()
    groups: dict[str, list[str]] = {}
    for f in record.flags:
        if f.status not in ("accepted", "needs_facts") or not f.missing_facts:
            continue
        doc = by_id[f.source_ids[0]].doc if f.source_ids and f.source_ids[0] in by_id else "?"
        group = f"Hearing {doc}" if doc in hearing_ids else f"Documents ({doc})"
        groups.setdefault(group, [])
        groups[group] += [q for q in f.missing_facts if q not in groups[group]]
    return dict(sorted(groups.items()))
