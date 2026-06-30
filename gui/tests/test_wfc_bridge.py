import _factorio_wfc as core
import pytest

from snapshot import (
    CELL_STRIDE,
    DIR_E,
    DIR_W,
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    build_minimal_catalog,
    create_cells_buffer,
    encode_cell_empty,
    encode_cell_undecided,
    set_cell_belt,
    set_cell_empty,
    set_cell_input_belt,
    set_cell_output_belt,
)
from wfc_bridge import ensure_catalog_loaded, validate


@pytest.fixture(autouse=True)
def _load_catalog():
    ensure_catalog_loaded()


def test_import_native_module():
    assert hasattr(core, "wire_format_version")
    assert hasattr(core, "load_catalog")
    assert hasattr(core, "validate_snapshot")
    assert core.wire_format_version() == 1


def test_minimal_catalog_roundtrip():
    blob = build_minimal_catalog()
    assert blob[:4] == b"FWFC"
    core.load_catalog(blob)


def test_cell_encodings():
    undecided = encode_cell_undecided()
    empty = encode_cell_empty()
    assert len(undecided) == CELL_STRIDE
    assert len(empty) == CELL_STRIDE
    assert undecided[0] == TAG_UNDECIDED
    assert empty[0] == TAG_EMPTY


def test_create_cells_buffer_defaults():
    cells = create_cells_buffer(3, 2)
    assert len(cells) == 3 * 2 * CELL_STRIDE
    assert all(cells[i * CELL_STRIDE] == TAG_UNDECIDED for i in range(6))


def test_validate_empty_grid():
    cells = create_cells_buffer(4, 3)
    is_valid, message = validate(4, 3, cells)
    assert is_valid is True
    assert message == ""


def test_validate_mixed_grid():
    cells = create_cells_buffer(3, 3)
    set_cell_empty(cells, 3, 0, 0)
    set_cell_empty(cells, 3, 2, 2)
    is_valid, message = validate(3, 3, cells)
    assert is_valid is True
    assert message == ""


def test_validate_rejects_wrong_buffer_size():
    cells = create_cells_buffer(2, 2)
    is_valid, message = validate(3, 3, cells)
    assert is_valid is False
    assert message


def test_format_cell_info_empty():
    from wfc_bridge import format_cell_info

    cells = create_cells_buffer(1, 1)
    set_cell_empty(cells, 1, 0, 0)
    text = format_cell_info(cells, 1, 1, 0, 0)
    assert "status: empty" in text
    assert "type: empty" in text


def test_format_cell_info_undecided():
    from wfc_bridge import format_cell_info

    cells = create_cells_buffer(1, 1)
    text = format_cell_info(cells, 1, 1, 0, 0)
    assert "status: undecided" in text


def test_format_cell_info_belt():
    from wfc_bridge import format_cell_info
    from snapshot import set_cell_belt

    cells = create_cells_buffer(2, 1)
    set_cell_belt(cells, 2, 0, 1, DIR_W, DIR_E, 0, 0xFFFFFFFF)
    text = format_cell_info(cells, 2, 1, 0, 1)
    assert "type: belt" in text
    assert "Cell (0,1)" in text
    assert "from: (0,0)" in text
    assert "to: (0,2)" in text
    assert "left lane: iron-plate" in text
    assert "right lane: (empty)" in text


def test_format_cell_info_input_output_belts():
    from wfc_bridge import format_cell_info

    cells = create_cells_buffer(3, 1)
    set_cell_input_belt(cells, 3, 0, 0, DIR_E, 0, EMPTY_ITEM_ID, 3.45, 0.0)
    set_cell_output_belt(cells, 3, 0, 2, DIR_W, EMPTY_ITEM_ID, 1, 0.0, 2.75)

    input_text = format_cell_info(cells, 3, 1, 0, 0)
    assert "type: input_belt" in input_text
    assert "to: (0,1)" in input_text
    assert "left lane: iron-plate @ 3.5" in input_text

    output_text = format_cell_info(cells, 3, 1, 0, 2)
    assert "type: output_belt" in output_text
    assert "from: (0,1)" in output_text
    assert "right lane: copper-plate @ 2.8" in output_text


def test_validate_input_belt_to_belt_snapshot_smoke():
    cells = create_cells_buffer(2, 1)
    set_cell_input_belt(cells, 2, 0, 0, DIR_E, EMPTY_ITEM_ID, 0, 0.0, 3.5)
    set_cell_belt(cells, 2, 0, 1, DIR_W, DIR_E, EMPTY_ITEM_ID, 0)

    is_valid, message = validate(2, 1, cells)
    assert is_valid is True
    assert message == ""
