from native_loader import load_native_module

load_native_module()

import _factorio_wfc as core

from snapshot import (
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    TYPE_ID_BELT,
    build_catalog_blob,
    build_minimal_catalog,
    get_cell_tag,
    is_cell_undecided,
    read_cell_belt,
)

EDITOR_ITEMS = ["iron-plate", "copper-plate", "iron-ore"]

_item_labels: list[str] = []


def ensure_catalog_loaded() -> None:
    global _item_labels
    blob = build_catalog_blob(items=EDITOR_ITEMS)
    core.load_catalog(blob)
    _item_labels = list(EDITOR_ITEMS)


def item_label(item_id: int) -> str:
    if item_id == EMPTY_ITEM_ID:
        return "(empty)"
    if 0 <= item_id < len(_item_labels):
        return _item_labels[item_id]
    return f"item#{item_id}"


def item_key_to_id(key: str) -> int:
    if key == "(empty)":
        return EMPTY_ITEM_ID
    return EDITOR_ITEMS.index(key)


def validate(width: int, height: int, cells: bytes | bytearray) -> tuple[bool, str]:
    result = core.validate_snapshot(width, height, cells)
    return result.is_valid, result.message


def _inspector_coords(col: int, row: int) -> tuple[int, int]:
    return row, col


def format_cell_info(cells: bytearray, width: int, height: int, x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= width or y >= height:
        return "No cell"

    ix, iy = _inspector_coords(x, y)
    tag = get_cell_tag(cells, width, x, y)
    if tag == TAG_UNDECIDED:
        return f"Cell ({ix},{iy})\n  status: undecided"

    if tag == TAG_EMPTY:
        return f"Cell ({ix},{iy})\n  status: empty\n  type: empty"

    if tag == TYPE_ID_BELT:
        belt = read_cell_belt(cells, width, x, y)
        if belt is None:
            return f"Cell ({ix},{iy})\n  status: occupied\n  type: belt (invalid payload)"
        from_ix, from_iy = _inspector_coords(belt.from_x, belt.from_y)
        to_ix, to_iy = _inspector_coords(belt.to_x, belt.to_y)
        lines = [
            f"Cell ({ix},{iy})",
            "  status: occupied",
            "  type: belt",
            f"  from: ({from_ix},{from_iy})",
            f"  to: ({to_ix},{to_iy})",
            f"  left lane: {item_label(belt.left_item_id)}",
            f"  right lane: {item_label(belt.right_item_id)}",
        ]
        return "\n".join(lines)

    return f"Cell ({ix},{iy})\n  status: occupied\n  type: unknown ({tag})"
