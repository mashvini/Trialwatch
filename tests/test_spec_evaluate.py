"""Spec for T10 (evaluation) against the demo answer key."""
from __future__ import annotations

import pytest
from helpers import DEMO, implemented_or_skip, oracle_lines

from fairtrace import evaluate
from fairtrace.schemas import Flag


def test_evaluate_scores_against_the_answer_key():
    key = evaluate.load_answer_key(DEMO)
    flags = [
        Flag(id="F1", right_id="examine_witnesses", source_ids=["H01-L012"], quote="x", explanation="x"),
        Flag(id="F2", right_id="public_hearing", source_ids=["H02-L005"], quote="x", explanation="x"),  # clean hearing
        Flag(id="F3", right_id="public_hearing", source_ids=["H01-L999"], quote="x", explanation="x"),  # bad citation
    ]
    result = implemented_or_skip(evaluate.evaluate, flags, key, {line.id for line in oracle_lines()})
    assert result["caught"] == ["A1"]
    assert "A7" not in result["missed"] and result["not_detectable"] == ["A7"]
    assert result["recall"] == pytest.approx(1 / 6)
    assert result["false_alarms"] == 1
    assert result["citation_rate"] == pytest.approx(2 / 3)
    assert result["flags_total"] == 3
