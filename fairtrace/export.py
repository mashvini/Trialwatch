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
    raise NotImplementedError("T9: export draft findings (see the docstring in export.py)")
