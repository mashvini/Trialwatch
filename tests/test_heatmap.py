"""T12: hearings × rights grid."""
from __future__ import annotations

from fairtrace.heatmap import DOCUMENTS_ROW, issue_grid
from fairtrace.schemas import Flag


def _cell(grid, hearing, right_id):
    return next(c for c in grid if c["hearing"] == hearing and c["right_id"] == right_id)


def test_grid_counts_flags_by_hearing_and_right(rights, demo_record, fixture_flags):
    grid = issue_grid(demo_record, rights, fixture_flags)
    assert _cell(grid, "H01", "examine_witnesses")["count"] == 2
    assert _cell(grid, "H02", "examine_witnesses")["count"] == 0
    assert len(grid) == 2 * len(rights)  # every hearing × right, zeros included; no empty documents row
    assert sum(c["count"] for c in grid) == len(fixture_flags)


def test_document_only_flags_get_their_own_row(rights, demo_record):
    ct = Flag(id="F-CT-1", right_id="reasoned_judgment", source_ids=["JDG-P003", "POL-P002"], quote="x", explanation="x")
    grid = issue_grid(demo_record, rights, [ct])
    assert _cell(grid, DOCUMENTS_ROW, "reasoned_judgment")["flags"] == "F-CT-1"
