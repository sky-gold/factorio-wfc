"""Wire format v1 encoder (Python side)."""

from __future__ import annotations

import struct
from dataclasses import dataclass

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
DIR_OFFSETS = ((0, -1), (1, 0), (0, 1), (-1, 0))

EMPTY_ITEM_ID = 0xFFFFFFFF

WIRE_MAGIC = b"FWFC"
WIRE_VERSION = 1
HEADER_SIZE = 16

SECTION_ITEMS = 0x01
SECTION_RECIPES = 0x02
SECTION_MACHINES = 0x03
SECTION_LOGISTICS = 0x04


def cell_index(width: int, x: int, y: int) -> int:
    return (y * width + x) * CELL_STRIDE


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
