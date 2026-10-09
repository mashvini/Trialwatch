"""Devil's Advocate: for each potential issue, the strongest justification the state could give,
and whether the record rebuts it. Counters confirmation bias before a report is published.
"""
from __future__ import annotations

from ..config import Settings
from ..schemas import CaseRecord, ChallengeSet
from .base import Analyzer


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
        raise NotImplementedError("T6: Devil's Advocate (see devils_advocate.py)")

    def apply(self, record: CaseRecord, result: ChallengeSet, settings: Settings) -> None:
        record.challenges = list(result.challenges)
