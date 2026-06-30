"""Wire format v1 encoder (Python side).

Grid coordinates: x = row (0 at top, increases downward), y = column (0 at left).
width = column count, height = row count.
"""

from __future__ import annotations

import json
import struct
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

CELL_STRIDE = 32
TAG_UNDECIDED = 0xFF
TAG_EMPTY = 0x00
TYPE_ID_BELT = 10

DIR_N = 0
DIR_E = 1
DIR_S = 2
DIR_W = 3

DIR_NAMES = ("North", "East", "South", "West")
DIR_LABELS = ("Up", "Right", "Down", "Left")
DIR_OFFSETS = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIR_BY_NAME = {name: index for index, name in enumerate(DIR_NAMES)}

EMPTY_ITEM_ID = 0xFFFFFFFF

WIRE_MAGIC = b"FWFC"
WIRE_VERSION = 1
HEADER_SIZE = 16

SECTION_ITEMS = 0x01
SECTION_RECIPES = 0x02
SECTION_MACHINES = 0x03
SECTION_LOGISTICS = 0x04


def cell_index(width: int, x: int, y: int) -> int:
    return (x * width + y) * CELL_STRIDE


def encode_cell_undecided() -> bytes:
    cell = bytearray(CELL_STRIDE)
    cell[0] = TAG_UNDECIDED
    return bytes(cell)


def encode_cell_empty() -> bytes:
    cell = bytearray(CELL_STRIDE)
    cell[0] = TAG_EMPTY
    return bytes(cell)


def create_cells_buffer(width: int, height: int) -> bytearray:
    buf = bytearray(width * height * CELL_STRIDE)
    for i in range(width * height):
        buf[i * CELL_STRIDE] = TAG_UNDECIDED
    return buf


def is_cell_undecided(cells: bytearray, width: int, x: int, y: int) -> bool:
    return cells[cell_index(width, x, y)] == TAG_UNDECIDED


def set_cell_undecided(cells: bytearray, width: int, x: int, y: int) -> None:
    offset = cell_index(width, x, y)
    cells[offset : offset + CELL_STRIDE] = encode_cell_undecided()


def set_cell_empty(cells: bytearray, width: int, x: int, y: int) -> None:
    offset = cell_index(width, x, y)
    cells[offset : offset + CELL_STRIDE] = encode_cell_empty()


def get_cell_tag(cells: bytearray, width: int, x: int, y: int) -> int:
    return cells[cell_index(width, x, y)]


def dir_to_cell(x: int, y: int, direction: int) -> tuple[int, int]:
    dx, dy = DIR_OFFSETS[direction]
    return x + dx, y + dy


def encode_cell_belt(
    from_dir: int,
    to_dir: int,
    left_item_id: int = EMPTY_ITEM_ID,
    right_item_id: int = EMPTY_ITEM_ID,
) -> bytes:
    cell = bytearray(CELL_STRIDE)
    cell[0] = TYPE_ID_BELT
    cell[1] = from_dir
    cell[2] = to_dir
    cell[3] = 0
    struct.pack_into("<I", cell, 4, left_item_id)
    struct.pack_into("<I", cell, 8, right_item_id)
    return bytes(cell)


def set_cell_belt(
    cells: bytearray,
    width: int,
    x: int,
    y: int,
    from_dir: int,
    to_dir: int,
    left_item_id: int = EMPTY_ITEM_ID,
    right_item_id: int = EMPTY_ITEM_ID,
) -> None:
    offset = cell_index(width, x, y)
    cells[offset : offset + CELL_STRIDE] = encode_cell_belt(
        from_dir, to_dir, left_item_id, right_item_id
    )


@dataclass(frozen=True)
class BeltCellInfo:
    from_x: int
    from_y: int
    to_x: int
    to_y: int
    left_item_id: int
    right_item_id: int


def read_cell_belt(cells: bytearray, width: int, x: int, y: int) -> BeltCellInfo | None:
    offset = cell_index(width, x, y)
    if cells[offset] != TYPE_ID_BELT:
        return None
    from_dir = cells[offset + 1]
    to_dir = cells[offset + 2]
    left_item_id = struct.unpack_from("<I", cells, offset + 4)[0]
    right_item_id = struct.unpack_from("<I", cells, offset + 8)[0]
    from_x, from_y = dir_to_cell(x, y, from_dir)
    to_x, to_y = dir_to_cell(x, y, to_dir)
    return BeltCellInfo(from_x, from_y, to_x, to_y, left_item_id, right_item_id)


GRID_EXPORT_FORMAT = "fwfc-grid-v1"


def _export_lane_item(
    item_id: int,
    item_label_fn: Callable[[int], str] | None,
) -> int | str | None:
    if item_id == EMPTY_ITEM_ID:
        return None
    if item_label_fn is not None:
        return item_label_fn(item_id)
    return item_id


def _import_lane_item(
    value: Any,
    item_key_to_id: Callable[[str], int] | None,
) -> int:
    if value is None:
        return EMPTY_ITEM_ID
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if item_key_to_id is None:
            raise ValueError(f"item key {value!r} requires item_key_to_id")
        return item_key_to_id(value)
    raise ValueError(f"invalid lane item value: {value!r}")


def _cell_to_export_dict(
    cells: bytearray,
    width: int,
    x: int,
    y: int,
    item_label_fn: Callable[[int], str] | None,
) -> dict[str, Any] | None:
    tag = get_cell_tag(cells, width, x, y)
    if tag == TAG_UNDECIDED:
        return None

    if tag == TAG_EMPTY:
        return {"x": x, "y": y, "type": "empty"}

    if tag == TYPE_ID_BELT:
        belt = read_cell_belt(cells, width, x, y)
        if belt is None:
            return {"x": x, "y": y, "type": "belt", "error": "invalid payload"}
        from_dir = cells[cell_index(width, x, y) + 1]
        to_dir = cells[cell_index(width, x, y) + 2]
        return {
            "x": x,
            "y": y,
            "type": "belt",
            "from_dir": DIR_NAMES[from_dir],
            "to_dir": DIR_NAMES[to_dir],
            "from": {"x": belt.from_x, "y": belt.from_y},
            "to": {"x": belt.to_x, "y": belt.to_y},
            "left_item": _export_lane_item(belt.left_item_id, item_label_fn),
            "right_item": _export_lane_item(belt.right_item_id, item_label_fn),
        }

    return {"x": x, "y": y, "type": "unknown", "type_id": tag}


def export_grid_json(
    width: int,
    height: int,
    cells: bytearray,
    *,
    item_label_fn: Callable[[int], str] | None = None,
) -> str:
    """Serialize decided cells to readable JSON (width=cols, height=rows)."""
    decided_cells: list[dict[str, Any]] = []
    for x in range(height):
        for y in range(width):
            cell_dict = _cell_to_export_dict(cells, width, x, y, item_label_fn)
            if cell_dict is not None:
                decided_cells.append(cell_dict)

    payload = {
        "format": GRID_EXPORT_FORMAT,
        "width": width,
        "height": height,
        "cells": decided_cells,
    }
    return json.dumps(payload, indent=2)


def _apply_import_cell(
    cells: bytearray,
    width: int,
    cell: dict[str, Any],
    item_key_to_id: Callable[[str], int] | None,
) -> None:
    x = int(cell["x"])
    y = int(cell["y"])
    cell_type = cell["type"]

    if cell_type == "empty":
        set_cell_empty(cells, width, x, y)
        return

    if cell_type == "belt":
        from_dir = DIR_BY_NAME[cell["from_dir"]]
        to_dir = DIR_BY_NAME[cell["to_dir"]]
        left_item_id = _import_lane_item(cell.get("left_item"), item_key_to_id)
        right_item_id = _import_lane_item(cell.get("right_item"), item_key_to_id)
        set_cell_belt(cells, width, x, y, from_dir, to_dir, left_item_id, right_item_id)
        return

    raise ValueError(f"unsupported cell type at ({x},{y}): {cell_type!r}")


def import_grid_json(
    text: str,
    *,
    item_key_to_id: Callable[[str], int] | None = None,
) -> tuple[int, int, bytearray]:
    """Restore grid from export_grid_json output."""
    payload = json.loads(text)
    if payload.get("format") != GRID_EXPORT_FORMAT:
        raise ValueError(f"unsupported export format: {payload.get('format')!r}")

    width = int(payload["width"])
    height = int(payload["height"])
    cells = create_cells_buffer(width, height)

    if "cells_b64" in payload:
        raise ValueError("legacy base64 export is no longer supported; re-export the grid")

    for cell in payload["cells"]:
        _apply_import_cell(cells, width, cell, item_key_to_id)

    return width, height, cells


def _encode_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<H", len(encoded)) + encoded


def _encode_section(section_id: int, payload: bytes) -> bytes:
    return struct.pack("<BI", section_id, len(payload)) + payload


def _encode_catalog_header() -> bytes:
    return WIRE_MAGIC + struct.pack("<HHI", WIRE_VERSION, 0, HEADER_SIZE) + b"\x00\x00\x00\x00"


def build_minimal_catalog() -> bytes:
    """Empty catalog (items section with count=0)."""
    items_payload = struct.pack("<I", 0)
    sections = _encode_section(SECTION_ITEMS, items_payload)
    return _encode_catalog_header() + sections


def build_catalog_blob(
    *,
    items: list[str] | None = None,
    recipes: list[dict] | None = None,
    machines: list[dict] | None = None,
    belt_speed: float = 0.0,
    inserter_speed: float = 0.0,
) -> bytes:
    """Build catalog blob for future use with game data."""
    sections = bytearray()

    item_list = items or []
    items_payload = bytearray(struct.pack("<I", len(item_list)))
    for item in item_list:
        items_payload.extend(_encode_string(item))
    sections.extend(_encode_section(SECTION_ITEMS, bytes(items_payload)))

    recipe_list = recipes or []
    recipes_payload = bytearray(struct.pack("<I", len(recipe_list)))
    for recipe in recipe_list:
        recipes_payload.extend(struct.pack("<Id", recipe["machine_item_index"], recipe["craft_time"]))
        inputs = recipe.get("inputs", [])
        recipes_payload.extend(struct.pack("<I", len(inputs)))
        for ing in inputs:
            recipes_payload.extend(struct.pack("<Id", ing["item_index"], ing["amount"]))
        outputs = recipe.get("outputs", [])
        recipes_payload.extend(struct.pack("<I", len(outputs)))
        for out in outputs:
            recipes_payload.extend(struct.pack("<Id", out["item_index"], out["amount"]))
    if recipe_list:
        sections.extend(_encode_section(SECTION_RECIPES, bytes(recipes_payload)))

    machine_list = machines or []
    machines_payload = bytearray(struct.pack("<I", len(machine_list)))
    for machine in machine_list:
        machines_payload.extend(
            struct.pack("<III", machine["item_index"], machine["width"], machine["height"])
        )
    if machine_list:
        sections.extend(_encode_section(SECTION_MACHINES, bytes(machines_payload)))

    logistics_payload = struct.pack("<dd", belt_speed, inserter_speed)
    if belt_speed or inserter_speed:
        sections.extend(_encode_section(SECTION_LOGISTICS, logistics_payload))

    header = _encode_catalog_header()
    return header + bytes(sections)
