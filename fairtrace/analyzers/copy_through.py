"""Copy-Through Detector: judgment passages copied word for word from the police report or
indictment. Plain text matching; no model, so it cannot invent anything.

Why section-aware: quoting the charges in the summary is normal; copying the police's
conclusions into the court's OWN REASONING is the warning sign (independence / reasoned judgment).
Compare documents only in the same language (never a translation against an original).
"""
from __future__ import annotations

from ..config import Settings
from ..schemas import CaseRecord, CopyReport, Flag
from .base import Analyzer

SOURCE_TYPES = ("indictment", "police_report")


def normalize_words(text: str) -> list[str]:
    """T7. Lowercase, turn punctuation into spaces, split on whitespace.

    Example: "Having considered the evidence, the court finds" ->
             ["having", "considered", "the", "evidence", "the", "court", "finds"]
    (Thai has no spaces between words: use a word segmenter such as PyThaiNLP, or character runs.)
    """
    raise NotImplementedError("T7: normalize words (see copy_through.py)")


def shared_runs(source_words: list[str], judgment_words: list[str], min_words: int) -> list[tuple[int, int, int]]:
    """T7. Common runs of at least `min_words` consecutive words, in order.

    Returns (start_in_source, start_in_judgment, length) triples. Use
    difflib.SequenceMatcher(None, source_words, judgment_words, autojunk=False).get_matching_blocks()
    and keep the blocks with size >= min_words. (SequenceMatcher returns non-overlapping blocks in
    order, which is enough here.)
    """
    raise NotImplementedError("T7: shared runs (see copy_through.py)")


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
        raise NotImplementedError("T7: copy-through matching (see copy_through.py)")

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
    raise NotImplementedError("T7: flags from copy-through matches (see copy_through.py)")
