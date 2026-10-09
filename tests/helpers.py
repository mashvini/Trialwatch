"""Shared test helpers."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from fairtrace import ingest
from fairtrace.schemas import SourceLine

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "data" / "demo_case"


def implemented_or_skip(fn, *args, **kwargs):
    """Call a function; skip the test (instead of failing) while it is still a stub.

    This is what makes the spec tests switch on by themselves once a task is built.
    """
    try:
        return fn(*args, **kwargs)
    except NotImplementedError as e:
        pytest.skip(f"not built yet: {e}")


def oracle_lines(case_dir: Path = DEMO) -> list[SourceLine]:
    """Reference numbering that mirrors the T1 spec.

    Used only so other tests (fixtures, verifier, Copy-Through...) don't depend on T1 being built.
    T1's own spec test checks that the real implementation produces exactly this.
    """
    case = ingest.load_case(case_dir)
    out: list[SourceLine] = []
    for hearing in case.hearings:
        text = (case_dir / hearing.file).read_text(encoding="utf-8")
        for n, raw in enumerate(text.splitlines(), start=1):
            line = raw.rstrip()
            if line and not line.startswith("#"):
                out.append(SourceLine(id=f"{hearing.id}-L{n:03d}", doc=hearing.id, text=line))
    for doc in case.documents:
        raw_lines = (case_dir / doc.file).read_text(encoding="utf-8").splitlines()
        body = "\n".join(line for line in raw_lines if not line.startswith("#"))
        paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip()]
        out += [SourceLine(id=f"{doc.id}-P{i:03d}", doc=doc.id, text=p) for i, p in enumerate(paragraphs, start=1)]
    return out
