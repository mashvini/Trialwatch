"""Devil's Advocate: for each potential issue, the strongest justification the state could give,
and whether the record rebuts it. Counters confirmation bias before a report is published.
"""
from __future__ import annotations

import json
import logging

import yaml

from .. import prompts, verify
from ..config import Settings
from ..schemas import CaseRecord, Challenge, ChallengeSet, Flag, SourceLine
from ..taxonomy import load_rights
from .base import Analyzer

log = logging.getLogger(__name__)


class DevilsAdvocate(Analyzer):
    id = "devils_advocate"
    label = "Devil's Advocate"
    description = "For each potential issue, writes the strongest justification the state could give, then checks whether the record rebuts it."
    stage = 2
    uses_model = True
    result_model = ChallengeSet

    def available(self, record: CaseRecord) -> tuple[bool, str]:
        if not [f for f in record.flags if f.status != "rejected"]:
            return False, "Needs potential issues first: build T2–T4, or run Copy-Through."
        return True, ""

    def run(self, record: CaseRecord, settings: Settings, llm) -> ChallengeSet:
        """T6. One model call per flag that isn't rejected.

        Steps for each flag:
        1. system, user_template, version = prompts.load_prompt(settings, "devils_advocate").
        2. Context lines: the flag's hearing lines (from its source_ids' prefixes) plus any cited
           document paragraphs; format with prompts.format_lines().
        3. user = prompts.render(user_template, flag=<flag JSON>, right=<the right's entry>, lines=...).
        4. challenges = llm.complete_model("devils_advocate", system, user, Challenge,
                                           key="challenges", mock_key=flag.id)
           In mock mode the shared fixture holds challenges for ALL flags: keep the one whose
           flag_id matches. Ignore any challenge for a different flag.
        5. Pass each kept challenge through verify.verify_challenge(challenge, record).
        Return ChallengeSet(challenges=[...]).

        Spec: tests/test_spec_devils_advocate.py
        """
        system, user_template, _version = prompts.load_prompt(settings, "devils_advocate")
        rights = {r.id: r for r in load_rights(settings)}
        challenges: list[Challenge] = []
        for flag in record.flags:
            if flag.status == "rejected":
                continue
            right = rights.get(flag.right_id)
            user = prompts.render(
                user_template,
                flag=json.dumps(flag.model_dump(exclude={"status", "verifier_notes"}), indent=1, ensure_ascii=False),
                right=yaml.safe_dump(right.model_dump(), sort_keys=False, allow_unicode=True) if right else flag.right_id,
                lines=prompts.format_lines(_context_lines(flag, record)),
            )
            raw = llm.complete_model("devils_advocate", system, user, Challenge, key="challenges", mock_key=flag.id)
            # The shared mock fixture (and a confused model) can return challenges for other flags.
            match = next((c for c in raw if c.flag_id == flag.id), None)
            if match is None:
                log.warning("Devil's Advocate returned no challenge for %s", flag.id)
                continue
            challenges.append(verify.verify_challenge(match, record))
        return ChallengeSet(challenges=challenges)

    def apply(self, record: CaseRecord, result: ChallengeSet, settings: Settings) -> None:
        record.challenges = list(result.challenges)


def _context_lines(flag: Flag, record: CaseRecord) -> list[SourceLine]:
    """All lines of every hearing the flag cites, plus the document paragraphs it cites."""
    hearing_ids = {h.id for h in record.case.hearings}
    by_id = record.lines_by_id()
    cited = [by_id[sid] for sid in flag.source_ids if sid in by_id]
    hearings = {line.doc for line in cited if line.doc in hearing_ids}
    paragraphs = {line.id for line in cited if line.doc not in hearing_ids}
    return [line for line in record.source_lines if line.doc in hearings or line.id in paragraphs]
