"""Copy-Through Detector: judgment passages copied word for word from the police report or
indictment. Plain text matching; no model, so it cannot invent anything.

Why section-aware: quoting the charges in the summary is normal; copying the police's
conclusions into the court's OWN REASONING is the warning sign (independence / reasoned judgment).
Compare documents only in the same language (never a translation against an original).
"""
from __future__ import annotations

import difflib
import re

from rapidfuzz import fuzz, process

from ..config import Settings
from ..ingest import paragraph_number
from ..schemas import CaseRecord, CopyMatch, CopyReport, Flag
from .base import Analyzer

SOURCE_TYPES = ("indictment", "police_report")
_PUNCTUATION = re.compile(r"[^\w\s]")


def normalize_words(text: str) -> list[str]:
    """T7. Lowercase, turn punctuation into spaces, split on whitespace.

    Example: "Having considered the evidence, the court finds" ->
             ["having", "considered", "the", "evidence", "the", "court", "finds"]
    (Thai has no spaces between words: use a word segmenter such as PyThaiNLP, or character runs.)
    """
    return _PUNCTUATION.sub(" ", text.lower()).split()


def shared_runs(source_words: list[str], judgment_words: list[str], min_words: int) -> list[tuple[int, int, int]]:
    """T7. Common runs of at least `min_words` consecutive words, in order.

    Returns (start_in_source, start_in_judgment, length) triples. Use
    difflib.SequenceMatcher(None, source_words, judgment_words, autojunk=False).get_matching_blocks()
    and keep the blocks with size >= min_words. (SequenceMatcher returns non-overlapping blocks in
    order, which is enough here.)
    """
    matcher = difflib.SequenceMatcher(None, source_words, judgment_words, autojunk=False)
    return [(b.a, b.b, b.size) for b in matcher.get_matching_blocks() if b.size >= min_words]


class CopyThrough(Analyzer):
    id = "copy_through"
    label = "Copy-Through Detector"
    description = "Finds judgment passages copied from the indictment or police report. Plain text matching, no AI."
    stage = 1
    uses_model = False
    result_model = CopyReport

    def available(self, record: CaseRecord) -> tuple[bool, str]:
        if not record.documents_of_type("judgment"):
            return False, "Needs a judgment: add it under documents in case.yaml."
        if not record.documents_of_type(*SOURCE_TYPES):
            return False, "Needs an indictment or police report to compare against."
        if not record.source_lines:
            return False, "Needs numbered sources first (T1 ingest)."
        return True, ""

    def params(self, settings: Settings) -> dict:
        return dict(settings.copy_through)

    def cache_inputs(self, record: CaseRecord) -> object:
        docs = {d.id for d in record.documents_of_type("judgment", *SOURCE_TYPES)}
        ranges = {d.id: d.reasoning_paragraphs for d in record.documents_of_type("judgment")}
        return {"lines": [l.model_dump() for l in record.source_lines if l.doc in docs], "ranges": ranges}

    def run(self, record: CaseRecord, settings: Settings, llm=None) -> CopyReport:
        """T7. Compare each judgment paragraph with the indictment / police report paragraphs.

        Thresholds come from settings.copy_through (config.yaml):
        1. Judgment paragraphs: record.lines_for(<judgment doc id>). Source paragraphs: every
           document of type indictment or police_report.
        2. normalize_words() every paragraph.
        3. For each judgment paragraph, pre-select the top `candidates_per_paragraph` source
           paragraphs with rapidfuzz.process.extract(..., scorer=fuzz.token_set_ratio).
        4. shared_runs(source, judgment, min_shared_words) for each candidate.
        5. One CopyMatch per (judgment paragraph, source paragraph) with at least one run:
           shared_text = words of the longest run joined by spaces, shared_words = its length,
           similarity = the token_set_ratio score,
           in_reasoning = paragraph number (ingest.paragraph_number) inside doc.reasoning_paragraphs.
        6. coverage_overall = judgment words inside any kept run / all judgment words (0-1).
           coverage_reasoning = the same within the reasoning paragraphs, or None if no range.

        Spec: tests/test_spec_copy_through.py
        """
        cfg = settings.copy_through
        sources = [
            (line.id, normalize_words(line.text))
            for doc in record.documents_of_type(*SOURCE_TYPES)
            for line in record.lines_for(doc.id)
        ]
        choices = [" ".join(words) for _, words in sources]
        matches: list[CopyMatch] = []
        covered = total = covered_reasoning = total_reasoning = 0
        has_range = False
        for doc in record.documents_of_type("judgment"):
            has_range = has_range or doc.reasoning_paragraphs is not None
            for para in record.lines_for(doc.id):
                words = normalize_words(para.text)
                in_reasoning = _in_range(paragraph_number(para.id), doc.reasoning_paragraphs)
                copied: set[int] = set()
                candidates = process.extract(
                    " ".join(words), choices, scorer=fuzz.token_set_ratio, limit=cfg["candidates_per_paragraph"]
                )
                for _, score, index in candidates:
                    source_id, source_words = sources[index]
                    runs = shared_runs(source_words, words, cfg["min_shared_words"])
                    if not runs:
                        continue
                    for _, start, size in runs:
                        copied.update(range(start, start + size))
                    _, start, size = max(runs, key=lambda run: run[2])
                    matches.append(
                        CopyMatch(
                            judgment_id=para.id,
                            source_id=source_id,
                            shared_text=" ".join(words[start : start + size]),
                            shared_words=size,
                            similarity=float(score),
                            in_reasoning=in_reasoning,
                        )
                    )
                covered += len(copied)
                total += len(words)
                if in_reasoning:
                    covered_reasoning += len(copied)
                    total_reasoning += len(words)
        return CopyReport(
            matches=matches,
            coverage_overall=covered / total if total else 0.0,
            coverage_reasoning=(covered_reasoning / total_reasoning if total_reasoning else 0.0) if has_range else None,
        )

    def apply(self, record: CaseRecord, result: CopyReport, settings: Settings) -> None:
        record.copy_report = result
        record.flags.extend(flags_from_report(result, settings))


def flags_from_report(report: CopyReport, settings: Settings) -> list[Flag]:
    """T7. Turn strong matches inside the court's reasoning into flags (template text, no model).

    For each match with in_reasoning and shared_words >= copy_through.flag_min_shared_words,
    in report order, create:
      Flag(id=f"F-CT-{n}", origin="copy_through", right_id=copy_through.right_id,
           source_ids=[match.judgment_id, match.source_id], quote=match.shared_text,
           explanation=("Potential issue: {judgment_id} of the judgment repeats {shared_words} words "
                        "of {source_id} word for word, inside the court's own reasoning. Check whether "
                        "the court assessed the evidence independently."),
           questions_for_lawyer=["Did the court assess this evidence independently?",
                                 "Does the judgment give its own reasons for this finding?"])
    Matches outside the reasoning section never become flags.

    Spec: tests/test_spec_copy_through.py
    """
    cfg = settings.copy_through
    strong = [m for m in report.matches if m.in_reasoning and m.shared_words >= cfg["flag_min_shared_words"]]
    return [
        Flag(
            id=f"F-CT-{n}",
            origin="copy_through",
            right_id=cfg["right_id"],
            source_ids=[m.judgment_id, m.source_id],
            quote=m.shared_text,
            explanation=(
                f"Potential issue: {m.judgment_id} of the judgment repeats {m.shared_words} words "
                f"of {m.source_id} word for word, inside the court's own reasoning. Check whether "
                "the court assessed the evidence independently."
            ),
            questions_for_lawyer=[
                "Did the court assess this evidence independently?",
                "Does the judgment give its own reasons for this finding?",
            ],
        )
        for n, m in enumerate(strong, start=1)
    ]


def _in_range(number: int, bounds: tuple[int, int] | None) -> bool:
    """Is paragraph `number` inside the inclusive (first, last) range?"""
    return bounds is not None and bounds[0] <= number <= bounds[1]
