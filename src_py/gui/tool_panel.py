"""Cell type selection and per-type parameter panels."""

from __future__ import annotations

from dataclasses import dataclass

import dearpygui.dearpygui as dpg

CELL_TYPE_LABELS = ["Empty"]
CELL_TYPE_VALUES = ["empty"]


@dataclass
class ToolState:
    cell_type: str = "empty"


def build_cell_type_panel(state: ToolState, on_change) -> None:
    dpg.add_text("Cell Type")
    dpg.add_radio_button(
        items=CELL_TYPE_LABELS,
        default_value=CELL_TYPE_LABELS[0],
        callback=lambda s, v: (_set_cell_type(state, v), on_change()),
        horizontal=False,
        tag="cell_type_radio",
    )


def build_cell_params_panel(state: ToolState) -> None:
    dpg.add_text("Cell Params")
    with dpg.group(tag="cell_params_group"):
        _show_params_for_type(state.cell_type)


def refresh_cell_params_panel(state: ToolState) -> None:
    if dpg.does_item_exist("cell_params_group"):
        dpg.delete_item("cell_params_group", children_only=True)
    _show_params_for_type(state.cell_type)


def _set_cell_type(state: ToolState, label: str) -> None:
    index = CELL_TYPE_LABELS.index(label) if label in CELL_TYPE_LABELS else 0
    state.cell_type = CELL_TYPE_VALUES[index]


def _show_params_for_type(cell_type: str) -> None:
    if cell_type == "empty":
        dpg.add_text("No parameters for Empty", parent="cell_params_group")
    else:
        dpg.add_text(f"No parameters for {cell_type}", parent="cell_params_group")


def apply_tool_to_cell(cells: bytearray, width: int, x: int, y: int, state: ToolState) -> None:
    from snapshot import set_cell_empty

    if state.cell_type == "empty":
        set_cell_empty(cells, width, x, y)
