"""Wire format v1 encoder (Python side)."""

from __future__ import annotations

import struct

CELL_STRIDE = 32
TAG_UNDECIDED = 0xFF
TAG_EMPTY = 0x00

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


def _encode_string(value: str) -> bytes:
    encoded = value.encode("utf-8")
    return struct.pack("<H", len(encoded)) + encoded


def _encode_section(section_id: int, payload: bytes) -> bytes:
    return struct.pack("<BI", section_id, len(payload)) + payload


def build_minimal_catalog() -> bytes:
    """Empty catalog (items section with count=0)."""
    items_payload = struct.pack("<I", 0)
    sections = _encode_section(SECTION_ITEMS, items_payload)
    header = WIRE_MAGIC + struct.pack("<HHI", WIRE_VERSION, 0, HEADER_SIZE)
    return header + sections


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

    header = WIRE_MAGIC + struct.pack("<HHI", WIRE_VERSION, 0, HEADER_SIZE)
    return header + bytes(sections)
