"""Ingest: load a case folder and number every line and paragraph.

Source IDs are the basis of every citation. They are created here and nowhere else.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .schemas import Case, DocumentRef, HearingRef, SourceLine


def load_case(case_dir: Path) -> Case:
    """Read <case_dir>/case.yaml into a Case."""
    data = yaml.safe_load((Path(case_dir) / "case.yaml").read_text(encoding="utf-8"))
    return Case.model_validate(data)


def number_hearing(hearing: HearingRef, text: str) -> list[SourceLine]:
    """T1. Turn one hearing's notes into numbered SourceLines.

    Spec (tests/test_spec_ingest.py):
    - id = f"{hearing.id}-L{n:03d}", where n is the PHYSICAL line number in the file, starting at 1.
    - Skip blank lines and lines starting with "#" (comments/metadata), but keep counting them,
      so "H01-L012" always means line 12 of the file, which a person can open and check.
    - doc = hearing.id
    - text = the line with trailing whitespace removed (otherwise unchanged).
    """
    raise NotImplementedError("T1: number hearing lines (see the docstring in ingest.py)")


def split_paragraphs(doc: DocumentRef, text: str) -> list[SourceLine]:
    """T1. Split a court document into numbered paragraphs.

    Spec (tests/test_spec_ingest.py):
    - Remove lines starting with "#" first.
    - Paragraphs are separated by one or more blank lines.
    - id = f"{doc.id}-P{n:03d}", where n counts paragraphs from 1.
    - Lines inside a paragraph are joined with single spaces; repeated whitespace collapses to one space.
    - doc = doc.id
    """
    raise NotImplementedError("T1: split document paragraphs (see the docstring in ingest.py)")


def read_sources(case_dir: Path, case: Case) -> list[SourceLine]:
    """Number every hearing and document listed in case.yaml (uses the two T1 functions)."""
    case_dir = Path(case_dir)
    lines: list[SourceLine] = []
    for hearing in case.hearings:
        lines += number_hearing(hearing, (case_dir / hearing.file).read_text(encoding="utf-8"))
    for doc in case.documents:
        lines += split_paragraphs(doc, (case_dir / doc.file).read_text(encoding="utf-8"))
    return lines


def paragraph_number(source_id: str) -> int:
    """'JDG-P034' -> 34."""
    return int(source_id.rsplit("-P", 1)[1])
