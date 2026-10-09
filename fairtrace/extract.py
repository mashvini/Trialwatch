"""Extract factual events from each hearing's numbered notes (model step 1 of 3)."""
from __future__ import annotations

import logging

from . import prompts
from .config import Settings
from .llm import LLM
from .schemas import CaseRecord, Event

log = logging.getLogger(__name__)


def extract_events(record: CaseRecord, llm: LLM, settings: Settings) -> list[Event]:
    """T2. One model call per hearing; returns events that cite only existing lines.

    Steps:
    1. For each hearing in record.case.hearings, take its lines: record.lines_for(hearing.id).
    2. system, user_template, version = prompts.load_prompt(settings, "extract").
    3. user = prompts.render(user_template, hearing_id=hearing.id, lines=prompts.format_lines(lines)).
    4. events = llm.complete_model("extract", system, user, Event, key="events", mock_key=hearing.id).
       (Optional, T11: redact names in `user` before the call.)
    5. Keep only source_ids of this hearing's lines (a subset of record.line_ids()); drop events left with none.
    6. Make ids unique: "E-H01-1", "E-H01-2", ...

    Spec: tests/test_spec_extract_flag.py
    """
    system, user_template, _version = prompts.load_prompt(settings, "extract")
    events: list[Event] = []
    for hearing in record.case.hearings:
        lines = record.lines_for(hearing.id)
        user = prompts.render(user_template, hearing_id=hearing.id, lines=prompts.format_lines(lines))
        raw = llm.complete_model("extract", system, user, Event, key="events", mock_key=hearing.id)
        # Only the lines this call was shown count: another hearing's ID here would be invented.
        events += _clean(raw, hearing.id, {line.id for line in lines})
    return events


def _clean(raw: list[Event], hearing_id: str, known_ids: set[str]) -> list[Event]:
    """Drop invented line IDs, drop events left with no citation, and assign ids in code."""
    kept: list[Event] = []
    for event in raw:
        valid = [sid for sid in event.source_ids if sid in known_ids]
        unknown = [sid for sid in event.source_ids if sid not in known_ids]
        if unknown:
            log.warning("%s: dropped unknown line IDs %s from event %r", hearing_id, unknown, event.action)
        if not valid:
            log.warning("%s: dropped event with no valid citation: %r", hearing_id, event.action)
            continue
        kept.append(
            event.model_copy(update={"id": f"E-{hearing_id}-{len(kept) + 1}", "hearing": hearing_id, "source_ids": valid})
        )
    return kept
