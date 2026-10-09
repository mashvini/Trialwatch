"""Data contracts shared by every module.

Change these only with the whole team's agreement: prompts, fixtures, tests and the
app all depend on them. See docs/03_solution_design.md for what each field means.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Actor = Literal[
    "judge", "prosecution", "defense", "defendant", "witness",
    "police", "court_staff", "monitor", "other",
]
FlagStatus = Literal["pending", "accepted", "rejected", "needs_facts"]
Verdict = Literal["rebutted", "not_addressed", "supported"]
DocType = Literal["indictment", "police_report", "judgment", "bail_decision", "evidence", "other"]


# ---------------------------------------------------------------- case definition (case.yaml)
class HearingRef(BaseModel):
    id: str                       # "H01"
    file: str                     # path relative to the case folder
    date: str | None = None       # ISO date, e.g. "2026-03-02"


class DocumentRef(BaseModel):
    id: str                       # "IND", "POL", "JDG", "BAIL"
    type: DocType
    file: str
    language: str = "en"
    # Judgments only: first and last paragraph (inclusive) of the court's own reasoning.
    reasoning_paragraphs: tuple[int, int] | None = None


class Case(BaseModel):
    id: str
    title: str
    country: str
    language: str = "en"
    synthetic: bool = False       # True = invented data; the app labels it everywhere
    charges: list[str] = []
    hearings: list[HearingRef] = []
    documents: list[DocumentRef] = []


# ---------------------------------------------------------------- pipeline records
class SourceLine(BaseModel):
    """One numbered line of notes or paragraph of a document. Created by ingest only, never by a model."""

    id: str                       # "H03-L047" (hearing H03, physical line 47) or "JDG-P034" (paragraph 34)
    doc: str                      # hearing or document id: "H03", "JDG"
    text: str


class Event(BaseModel):
    """A factual courtroom event, with no legal conclusions."""

    id: str                       # "E-H01-1"
    hearing: str
    actor: Actor
    action: str
    source_ids: list[str]


class Flag(BaseModel):
    """A potential fair-trial issue for a lawyer to review."""

    id: str                                   # "F-H01-1", Copy-Through: "F-CT-1"
    right_id: str                             # must exist in taxonomy/rights.yaml
    origin: Literal["notes", "copy_through"] = "notes"
    event_ids: list[str] = []
    source_ids: list[str]                     # must exist; checked by verify.py
    quote: str                                # must match one of the cited lines
    explanation: str                          # "potential issue" language, never "violation"
    questions_for_lawyer: list[str] = []
    missing_facts: list[str] = []             # become questions for the monitor (Gap Finder)
    status: FlagStatus = "pending"
    verifier_notes: list[str] = []            # filled by verify.py


class Challenge(BaseModel):
    """Devil's Advocate result for one flag."""

    flag_id: str
    state_argument: str                       # may be hypothetical: what the state COULD argue
    verdict: Verdict                          # does the record rebut it, support it, or not address it?
    source_ids: list[str] = []                # required for rebutted/supported (see verify.verify_challenge)
    reasoning: str = ""


class ChallengeSet(BaseModel):
    challenges: list[Challenge] = []


class CopyMatch(BaseModel):
    """One judgment paragraph vs one source paragraph (Copy-Through Detector)."""

    judgment_id: str                          # "JDG-P003"
    source_id: str                            # "POL-P002" or "IND-P002"
    shared_text: str                          # words of the longest shared run (normalized)
    shared_words: int
    similarity: float                         # 0-100 paragraph similarity (rapidfuzz)
    in_reasoning: bool                        # inside the judgment's reasoning_paragraphs?


class CopyReport(BaseModel):
    matches: list[CopyMatch] = []
    coverage_overall: float = 0.0             # share of judgment words inside copied runs, 0-1
    coverage_reasoning: float | None = None   # same, within the reasoning section (None if no range)


class Decision(BaseModel):
    """One line of data/<case>/audit_log.jsonl."""

    flag_id: str
    decision: FlagStatus
    reviewer: str
    note: str = ""
    model: str = ""
    prompt_version: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------- everything known about one case
class CaseRecord(BaseModel):
    case: Case
    source_lines: list[SourceLine] = []
    events: list[Event] = []
    flags: list[Flag] = []
    challenges: list[Challenge] = []
    copy_report: CopyReport | None = None

    def line_ids(self) -> set[str]:
        return {line.id for line in self.source_lines}

    def lines_by_id(self) -> dict[str, SourceLine]:
        return {line.id: line for line in self.source_lines}

    def lines_for(self, doc_id: str) -> list[SourceLine]:
        return [line for line in self.source_lines if line.doc == doc_id]

    def documents_of_type(self, *types: str) -> list[DocumentRef]:
        return [d for d in self.case.documents if d.type in types]
