import logging

from native_loader import MODULE_NAME, load_native_module

log = logging.getLogger(__name__)

log.info("wfc_bridge: loading native module ...")
if not load_native_module():
    raise ImportError(
        f"Could not load {MODULE_NAME}. "
        "Run make.bat build and ensure build/Release contains the .pyd file."
    )

import _factorio_wfc as core  # noqa: E402

log.info("wfc_bridge: _factorio_wfc import OK")

from snapshot import (  # noqa: E402
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    TYPE_ID_BELT,
    TYPE_ID_INPUT_BELT,
    TYPE_ID_OUTPUT_BELT,
    build_catalog_blob,
    build_minimal_catalog,
    get_cell_tag,
    is_cell_undecided,
    read_cell_belt,
    read_cell_input_belt,
    read_cell_output_belt,
)

EDITOR_ITEMS = ["iron-plate", "copper-plate", "iron-ore"]

_item_labels: list[str] = []


def ensure_catalog_loaded() -> None:
    global _item_labels
    log.info("Loading session catalog (%d items) ...", len(EDITOR_ITEMS))
    blob = build_catalog_blob(items=EDITOR_ITEMS)
    core.load_catalog(blob)
    _item_labels = list(EDITOR_ITEMS)
    log.info("Catalog loaded OK")


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
    log.debug("validate(%s cols x %s rows, %s bytes)", width, height, len(cells))
    result = core.validate_snapshot(width, height, cells)
    log.debug("validate -> is_valid=%s message=%r", result.is_valid, result.message)
    return result.is_valid, result.message


def format_cell_info(cells: bytearray, width: int, height: int, x: int, y: int) -> str:
    if x < 0 or y < 0 or x >= height or y >= width:
        return "No cell"

    tag = get_cell_tag(cells, width, x, y)
    if tag == TAG_UNDECIDED:
        return f"Cell ({x},{y})\n  status: undecided"

    if tag == TAG_EMPTY:
        return f"Cell ({x},{y})\n  status: empty\n  type: empty"

    if tag == TYPE_ID_BELT:
        belt = read_cell_belt(cells, width, x, y)
        if belt is None:
            return f"Cell ({x},{y})\n  status: occupied\n  type: belt (invalid payload)"
        lines = [
            f"Cell ({x},{y})",
            "  status: occupied",
            "  type: belt",
            f"  from: ({belt.from_x},{belt.from_y})",
            f"  to: ({belt.to_x},{belt.to_y})",
            f"  left lane: {item_label(belt.left_item_id)}",
            f"  right lane: {item_label(belt.right_item_id)}",
        ]
        return "\n".join(lines)

    if tag == TYPE_ID_INPUT_BELT:
        input_belt = read_cell_input_belt(cells, width, x, y)
        if input_belt is None:
            return f"Cell ({x},{y})\n  status: occupied\n  type: input_belt (invalid payload)"
        lines = [
            f"Cell ({x},{y})",
            "  status: occupied",
            "  type: input_belt",
            f"  to: ({input_belt.to_x},{input_belt.to_y})",
            f"  left lane: {item_label(input_belt.left_item_id)} @ {input_belt.left_max_rate:.1f}",
            f"  right lane: {item_label(input_belt.right_item_id)} @ {input_belt.right_max_rate:.1f}",
        ]
        return "\n".join(lines)

    if tag == TYPE_ID_OUTPUT_BELT:
        output_belt = read_cell_output_belt(cells, width, x, y)
        if output_belt is None:
            return f"Cell ({x},{y})\n  status: occupied\n  type: output_belt (invalid payload)"
        lines = [
            f"Cell ({x},{y})",
            "  status: occupied",
            "  type: output_belt",
            f"  from: ({output_belt.from_x},{output_belt.from_y})",
            f"  left lane: {item_label(output_belt.left_item_id)} @ {output_belt.left_min_rate:.1f}",
            f"  right lane: {item_label(output_belt.right_item_id)} @ {output_belt.right_min_rate:.1f}",
        ]
        return "\n".join(lines)

    return f"Cell ({x},{y})\n  status: occupied\n  type: unknown ({tag})"


def worst_case_inspector_body() -> str:
    """Largest inspector body text (belt with wide coordinates and item names)."""
    longest_item = max(EDITOR_ITEMS, key=len) if EDITOR_ITEMS else "item#99999"
    return "\n".join(
        [
            "Cell (99,99)",
            "  status: occupied",
            "  type: belt",
            "  from: (99,99)",
            "  to: (99,99)",
            f"  left lane: {longest_item}",
            f"  right lane: {longest_item} @ 999.9",
        ]
    )
