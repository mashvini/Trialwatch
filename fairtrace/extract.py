"""Extract factual events from each hearing's numbered notes (model step 1 of 3)."""
from __future__ import annotations

from .config import Settings
from .llm import LLM
from .schemas import CaseRecord, Event


def extract_events(record: CaseRecord, llm: LLM, settings: Settings) -> list[Event]:
    """T2. One model call per hearing; returns events that cite only existing lines.

    Steps:
    1. For each hearing in record.case.hearings, take its lines: record.lines_for(hearing.id).
    2. system, user_template, version = prompts.load_prompt(settings, "extract").
    3. user = prompts.render(user_template, hearing_id=hearing.id, lines=prompts.format_lines(lines)).
    4. events = llm.complete_model("extract", system, user, Event, key="events", mock_key=hearing.id).
       (Optional, T11: redact names in `user` before the call.)
    5. Keep only source_ids that exist in record.line_ids(); drop events left with none.
    6. Make ids unique: "E-H01-1", "E-H01-2", ...

    Spec: tests/test_spec_extract_flag.py
    """
    raise NotImplementedError("T2: extract events (see the docstring in extract.py)")
