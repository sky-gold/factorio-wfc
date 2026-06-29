import struct

from snapshot import (
    CELL_STRIDE,
    DIR_E,
    DIR_W,
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    TYPE_ID_BELT,
    create_cells_buffer,
    encode_cell_belt,
    read_cell_belt,
    set_cell_belt,
    set_cell_empty,
)


def test_snapshot_golden_bytes():
    """Golden vector: 2x1 grid [empty, undecided]."""
    cells = create_cells_buffer(2, 1)
    set_cell_empty(cells, 2, 0, 0)
    assert cells[0] == TAG_EMPTY
    assert cells[CELL_STRIDE] == TAG_UNDECIDED


def test_belt_golden_bytes_straight():
    cell = encode_cell_belt(DIR_W, DIR_E)
    assert len(cell) == CELL_STRIDE
    assert cell[0] == TYPE_ID_BELT
    assert cell[1] == DIR_W
    assert cell[2] == DIR_E
    assert cell[3] == 0
    assert struct.unpack_from("<I", cell, 4)[0] == EMPTY_ITEM_ID
    assert struct.unpack_from("<I", cell, 8)[0] == EMPTY_ITEM_ID


def test_belt_roundtrip_straight():
    cells = create_cells_buffer(3, 1)
    set_cell_belt(cells, 3, 1, 0, DIR_W, DIR_E, 1, 2)
    belt = read_cell_belt(cells, 3, 1, 0)
    assert belt is not None
    assert belt.from_x == 0 and belt.from_y == 0
    assert belt.to_x == 2 and belt.to_y == 0
    assert belt.left_item_id == 1
    assert belt.right_item_id == 2


def test_belt_roundtrip_corner():
    from snapshot import DIR_S

    cells = create_cells_buffer(1, 1)
    set_cell_belt(cells, 1, 0, 0, DIR_S, DIR_E)
    belt = read_cell_belt(cells, 1, 0, 0)
    assert belt is not None
    assert belt.from_x == 0 and belt.from_y == 1
    assert belt.to_x == 1 and belt.to_y == 0
