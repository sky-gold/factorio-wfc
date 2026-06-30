import struct

from snapshot import (
    CELL_STRIDE,
    DIR_E,
    DIR_W,
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    TYPE_ID_BELT,
    TYPE_ID_INPUT_BELT,
    TYPE_ID_OUTPUT_BELT,
    create_cells_buffer,
    encode_cell_belt,
    encode_cell_input_belt,
    encode_cell_output_belt,
    read_cell_belt,
    read_cell_input_belt,
    read_cell_output_belt,
    set_cell_belt,
    set_cell_empty,
    set_cell_input_belt,
    set_cell_output_belt,
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


def test_input_output_belt_golden_bytes():
    input_cell = encode_cell_input_belt(DIR_E, 1, 2, 3.5, 4.25)
    assert len(input_cell) == CELL_STRIDE
    assert input_cell[0] == TYPE_ID_INPUT_BELT
    assert input_cell[1] == DIR_E
    assert struct.unpack_from("<I", input_cell, 4)[0] == 1
    assert struct.unpack_from("<I", input_cell, 8)[0] == 2
    assert struct.unpack_from("<d", input_cell, 12)[0] == 3.5
    assert struct.unpack_from("<d", input_cell, 20)[0] == 4.25

    output_cell = encode_cell_output_belt(DIR_W, 1, 2, 1.5, 2.75)
    assert len(output_cell) == CELL_STRIDE
    assert output_cell[0] == TYPE_ID_OUTPUT_BELT
    assert output_cell[1] == DIR_W
    assert struct.unpack_from("<I", output_cell, 4)[0] == 1
    assert struct.unpack_from("<I", output_cell, 8)[0] == 2
    assert struct.unpack_from("<d", output_cell, 12)[0] == 1.5
    assert struct.unpack_from("<d", output_cell, 20)[0] == 2.75


def test_belt_roundtrip_straight():
    cells = create_cells_buffer(3, 1)
    set_cell_belt(cells, 3, 0, 1, DIR_W, DIR_E, 1, 2)
    belt = read_cell_belt(cells, 3, 0, 1)
    assert belt is not None
    assert belt.from_x == 0 and belt.from_y == 0
    assert belt.to_x == 0 and belt.to_y == 2
    assert belt.left_item_id == 1
    assert belt.right_item_id == 2


def test_input_output_belt_roundtrip():
    cells = create_cells_buffer(3, 1)
    set_cell_input_belt(cells, 3, 0, 0, DIR_E, 1, 2, 3.5, 4.25)
    set_cell_output_belt(cells, 3, 0, 2, DIR_W, 1, 2, 1.5, 2.75)

    input_belt = read_cell_input_belt(cells, 3, 0, 0)
    assert input_belt is not None
    assert input_belt.to_x == 0 and input_belt.to_y == 1
    assert input_belt.left_item_id == 1
    assert input_belt.right_item_id == 2
    assert input_belt.left_max_rate == 3.5
    assert input_belt.right_max_rate == 4.25

    output_belt = read_cell_output_belt(cells, 3, 0, 2)
    assert output_belt is not None
    assert output_belt.from_x == 0 and output_belt.from_y == 1
    assert output_belt.left_item_id == 1
    assert output_belt.right_item_id == 2
    assert output_belt.left_min_rate == 1.5
    assert output_belt.right_min_rate == 2.75


def test_belt_roundtrip_corner():
    from snapshot import DIR_S

    cells = create_cells_buffer(1, 1)
    set_cell_belt(cells, 1, 0, 0, DIR_S, DIR_E)
    belt = read_cell_belt(cells, 1, 0, 0)
    assert belt is not None
    assert belt.from_x == 1 and belt.from_y == 0
    assert belt.to_x == 0 and belt.to_y == 1


def test_export_grid_json_roundtrip():
    from snapshot import export_grid_json, import_grid_json, set_cell_belt

    def item_label(item_id: int) -> str:
        return {1: "iron-plate", 2: "copper-plate"}[item_id]

    def item_key_to_id(key: str) -> int:
        return {"iron-plate": 1, "copper-plate": 2}[key]

    cells = create_cells_buffer(3, 2)
    set_cell_empty(cells, 3, 0, 0)
    set_cell_belt(cells, 3, 0, 1, DIR_W, DIR_E, 1, 2)
    set_cell_input_belt(cells, 3, 1, 0, DIR_E, 1, EMPTY_ITEM_ID, 3.5, 0.0)
    set_cell_output_belt(cells, 3, 1, 2, DIR_W, EMPTY_ITEM_ID, 2, 0.0, 2.75)
    text = export_grid_json(3, 2, cells, item_label_fn=item_label)
    assert '"type": "empty"' in text
    assert '"left_item": "iron-plate"' in text
    assert '"right_item": "copper-plate"' in text
    assert '"type": "input_belt"' in text
    assert '"left_max_rate": 3.5' in text
    assert '"type": "output_belt"' in text
    assert '"right_min_rate": 2.75' in text
    assert "cells_b64" not in text

    width, height, restored = import_grid_json(text, item_key_to_id=item_key_to_id)
    assert width == 3
    assert height == 2
    assert restored == cells
