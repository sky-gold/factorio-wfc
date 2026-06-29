"""Cell type selection and per-type parameter panels."""

from __future__ import annotations

from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from snapshot import DIR_E, DIR_LABELS, DIR_W
from wfc_bridge import EDITOR_ITEMS, item_key_to_id

CELL_TYPE_LABELS = ["Empty", "Belt"]
CELL_TYPE_VALUES = ["empty", "belt"]

LANE_ITEM_CHOICES = ["(empty)"] + EDITOR_ITEMS


@dataclass
class ToolState:
    cell_type: str = "empty"
    from_dir: int = DIR_W
    to_dir: int = DIR_E
    left_item_key: str = "(empty)"
    right_item_key: str = "(empty)"


def build_cell_type_panel(state: ToolState, on_change) -> None:
    dpg.add_text("Cell Type")
    default_index = CELL_TYPE_VALUES.index(state.cell_type) if state.cell_type in CELL_TYPE_VALUES else 0
    dpg.add_radio_button(
        items=CELL_TYPE_LABELS,
        default_value=CELL_TYPE_LABELS[default_index],
        callback=lambda s, v: (_set_cell_type(state, v), on_change()),
        horizontal=False,
        tag="cell_type_radio",
    )


def build_cell_params_panel(state: ToolState) -> None:
    dpg.add_text("Cell Params")
    with dpg.group(tag="cell_params_group"):
        _show_params_for_type(state)


def refresh_cell_params_panel(state: ToolState) -> None:
    if dpg.does_item_exist("cell_params_group"):
        dpg.delete_item("cell_params_group", children_only=True)
    _show_params_for_type(state)


def _set_cell_type(state: ToolState, label: str) -> None:
    index = CELL_TYPE_LABELS.index(label) if label in CELL_TYPE_LABELS else 0
    state.cell_type = CELL_TYPE_VALUES[index]


def _show_params_for_type(state: ToolState) -> None:
    if state.cell_type == "empty":
        dpg.add_text("No parameters for Empty", parent="cell_params_group")
        return

    if state.cell_type == "belt":
        dpg.add_text("From direction", parent="cell_params_group")
        dpg.add_combo(
            items=list(DIR_LABELS),
            default_value=DIR_LABELS[state.from_dir],
            callback=lambda s, v: setattr(state, "from_dir", DIR_LABELS.index(v)),
            parent="cell_params_group",
            tag="belt_from_dir",
        )
        dpg.add_text("To direction", parent="cell_params_group")
        dpg.add_combo(
            items=list(DIR_LABELS),
            default_value=DIR_LABELS[state.to_dir],
            callback=lambda s, v: setattr(state, "to_dir", DIR_LABELS.index(v)),
            parent="cell_params_group",
            tag="belt_to_dir",
        )
        dpg.add_text("Left lane", parent="cell_params_group")
        dpg.add_combo(
            items=LANE_ITEM_CHOICES,
            default_value=state.left_item_key,
            callback=lambda s, v: setattr(state, "left_item_key", v),
            parent="cell_params_group",
            tag="belt_left_item",
        )
        dpg.add_text("Right lane", parent="cell_params_group")
        dpg.add_combo(
            items=LANE_ITEM_CHOICES,
            default_value=state.right_item_key,
            callback=lambda s, v: setattr(state, "right_item_key", v),
            parent="cell_params_group",
            tag="belt_right_item",
        )
        return

    dpg.add_text(f"No parameters for {state.cell_type}", parent="cell_params_group")


def apply_tool_to_cell(cells: bytearray, width: int, x: int, y: int, state: ToolState) -> None:
    from snapshot import set_cell_belt, set_cell_empty

    if state.cell_type == "empty":
        set_cell_empty(cells, width, x, y)
    elif state.cell_type == "belt":
        set_cell_belt(
            cells,
            width,
            x,
            y,
            state.from_dir,
            state.to_dir,
            item_key_to_id(state.left_item_key),
            item_key_to_id(state.right_item_key),
        )
