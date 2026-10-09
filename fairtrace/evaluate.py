"""Measure flags against a lawyer-written answer key (data/<case>/answer_key.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

from .schemas import Flag


class AnswerItem(BaseModel):
    id: str
    right_id: str
    source_ids: list[str]
    note: str = ""
    detectable_by_mvp: bool = True     # False = needs analysis we haven't built; not counted in recall


class AnswerKey(BaseModel):
    case_id: str
    expected: list[AnswerItem] = []
    clean_hearings: list[str] = []     # any flag citing these hearings is a false alarm


def load_answer_key(case_dir: Path) -> AnswerKey | None:
    path = Path(case_dir) / "answer_key.yaml"
    if not path.exists():
        return None
    return AnswerKey.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def evaluate(flags: list[Flag], key: AnswerKey, line_ids: set[str]) -> dict:
    """T10. Score flags against the answer key.

    Spec (tests/test_spec_evaluate.py):
    - An expected item is "caught" if any flag has the same right_id and shares >= 1 source id.
    - recall = caught / number of expected items with detectable_by_mvp=True (0.0 if none);
      only detectable items count toward caught and missed.
    - false_alarms = number of flags citing any line of a clean hearing (id starts with "<hearing>-L").
    - citation_rate = share of flags whose source_ids all exist in line_ids (1.0 if no flags).
    Return:
      {"caught": [item ids], "missed": [item ids], "recall": float,
       "false_alarms": int, "citation_rate": float, "flags_total": int,
       "not_detectable": [item ids with detectable_by_mvp=False]}
    """
    detectable = [item for item in key.expected if item.detectable_by_mvp]
    caught = [item.id for item in detectable if _is_caught(item, flags)]
    clean_prefixes = tuple(f"{h}-L" for h in key.clean_hearings)
    return {
        "caught": caught,
        "missed": [item.id for item in detectable if item.id not in caught],
        "recall": len(caught) / len(detectable) if detectable else 0.0,
        "false_alarms": sum(1 for f in flags if clean_prefixes and any(s.startswith(clean_prefixes) for s in f.source_ids)),
        "citation_rate": sum(1 for f in flags if set(f.source_ids) <= line_ids) / len(flags) if flags else 1.0,
        "flags_total": len(flags),
        "not_detectable": [item.id for item in key.expected if not item.detectable_by_mvp],
    }


def _is_caught(item: AnswerItem, flags: list[Flag]) -> bool:
    """Same right and at least one shared source id."""
    return any(f.right_id == item.right_id and set(f.source_ids) & set(item.source_ids) for f in flags)
