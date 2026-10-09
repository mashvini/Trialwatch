"""Hearings × rights grid (T12): where potential issues cluster across a case. Plain counting, no model."""
from __future__ import annotations

from .schemas import CaseRecord, Flag
from .taxonomy import Right

DOCUMENTS_ROW = "Court documents"


def issue_grid(record: CaseRecord, rights: list[Right], flags: list[Flag]) -> list[dict]:
    """One cell per (hearing, right): how many of `flags` cite that hearing, and which.

    Rows follow the case's hearing order, plus a "Court documents" row for flags that cite only
    documents (Copy-Through). A flag citing two hearings counts in both. Every cell is returned,
    zeros included, so a right with no potential issues still shows as an empty column.
    """
    by_id = record.lines_by_id()
    hearing_ids = [h.id for h in record.case.hearings]
    rows = hearing_ids + [DOCUMENTS_ROW]
    cells = {(row, r.id): [] for row in rows for r in rights}
    for f in flags:
        docs = {by_id[sid].doc for sid in f.source_ids if sid in by_id}
        hearings = [h for h in hearing_ids if h in docs]
        for row in hearings or ([DOCUMENTS_ROW] if docs else []):
            if (row, f.right_id) in cells:
                cells[(row, f.right_id)].append(f.id)
    names = {r.id: r.name for r in rights}
    return [
        {"hearing": row, "right_id": right_id, "right": names[right_id], "count": len(ids), "flags": ", ".join(ids)}
        for (row, right_id), ids in cells.items()
        if row != DOCUMENTS_ROW or any(cells[(DOCUMENTS_ROW, r.id)] for r in rights)  # hide an empty documents row
    ]
