"""Map events to potential fair-trial issues (model step 2 of 3)."""
from __future__ import annotations

import json

from . import prompts, taxonomy
from .config import Settings
from .llm import LLM
from .schemas import CaseRecord, Flag
from .taxonomy import Right


def flag_issues(record: CaseRecord, llm: LLM, settings: Settings, rights: list[Right]) -> list[Flag]:
    """T3. One model call per hearing; returns flags for the verifier.

    Steps:
    1. For each hearing: its lines (record.lines_for(hearing.id)) and its events (event.hearing == hearing.id).
    2. system, user_template, version = prompts.load_prompt(settings, "flag").
    3. Fill the placeholders with prompts.render():
         hearing_id, rights=taxonomy.rights_for_prompt(rights),
         examples=taxonomy.load_worked_examples(settings),
         events=<events as JSON>, lines=prompts.format_lines(lines)
    4. flags = llm.complete_model("flag", system, user, Flag, key="flags", mock_key=hearing.id)
    5. Set origin="notes" and status="pending"; make ids unique ("F-H01-1", ...).
    6. Optional: if verify.banned_words_in(explanation) finds conclusory words, re-ask once.

    Do NOT filter here: verify.verify_flags decides what passes, so rejections stay visible.
    Spec: tests/test_spec_extract_flag.py
    """
    system, user_template, _version = prompts.load_prompt(settings, "flag")
    rights_text = taxonomy.rights_for_prompt(rights)
    examples = taxonomy.load_worked_examples(settings)
    flags: list[Flag] = []
    for hearing in record.case.hearings:
        events = [e.model_dump() for e in record.events if e.hearing == hearing.id]
        user = prompts.render(
            user_template,
            hearing_id=hearing.id,
            rights=rights_text,
            examples=examples,
            events=json.dumps(events, indent=1, ensure_ascii=False),
            lines=prompts.format_lines(record.lines_for(hearing.id)),
        )
        raw = llm.complete_model("flag", system, user, Flag, key="flags", mock_key=hearing.id)
        # ids, origin and status are set in code, never taken from the model.
        flags += [
            f.model_copy(update={"id": f"F-{hearing.id}-{n}", "origin": "notes", "status": "pending", "verifier_notes": []})
            for n, f in enumerate(raw, start=1)
        ]
    return flags
