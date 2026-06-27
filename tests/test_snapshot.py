def test_snapshot_golden_bytes():
    """Golden vector: 2x1 grid [empty, undecided]."""
    from snapshot import CELL_STRIDE, TAG_EMPTY, TAG_UNDECIDED, create_cells_buffer, set_cell_empty

    cells = create_cells_buffer(2, 1)
    set_cell_empty(cells, 2, 0, 0)
    assert cells[0] == TAG_EMPTY
    assert cells[CELL_STRIDE] == TAG_UNDECIDED
