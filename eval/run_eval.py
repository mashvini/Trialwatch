"""Score a case from the command line, without the app.

Usage:  python -m eval.run_eval data/demo_case [mock|api|local]

Runs ingest → extract → flag → verify (+ Copy-Through if enabled) and prints the evaluation.
Needs T1–T4 and T10 to be built; until then it says which step is missing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from fairtrace import evaluate, extract, flag, ingest, redact, verify
from fairtrace.analyzers import REGISTRY
from fairtrace.config import load_settings
from fairtrace.llm import LLM
from fairtrace.schemas import CaseRecord
from fairtrace.taxonomy import load_rights


def score(case_dir: Path, mode: str | None = None) -> dict | None:
    """Run the pipeline on one case and score it; None if the case has no answer key."""
    settings = load_settings()
    rights = load_rights(settings)
    case = ingest.load_case(case_dir)
    llm = LLM(settings, mode, case_id=case.id)
    record = CaseRecord(case=case)
    record.source_lines = redact.redact_lines(ingest.read_sources(case_dir, case), redact.load_names(case_dir))
    record.events = extract.extract_events(record, llm, settings)
    record.flags = flag.flag_issues(record, llm, settings, rights)
    record.flags, rejected = verify.verify_flags(record.flags, record, settings, rights)
    ct = REGISTRY["copy_through"]
    if "copy_through" in settings.analyzers_enabled and ct.available(record)[0]:
        ct.apply(record, ct.run(record, settings, llm), settings)
    key = evaluate.load_answer_key(case_dir)
    if key is None:
        return None
    result = evaluate.evaluate(record.flags, key, record.line_ids())
    result["rejected_by_verifier"] = [f.id for f in rejected]
    return result


def main(case_dir: Path, mode: str | None = None) -> int:
    try:
        result = score(case_dir, mode)
    except NotImplementedError as e:
        print("Not built yet:", e)
        return 2
    if result is None:
        print("No answer_key.yaml in", case_dir)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None))
