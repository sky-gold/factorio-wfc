"""Hover cell inspector panel."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from wfc_bridge import format_cell_info


def update_inspector(tag: str, cells: bytearray, width: int, height: int, x: int, y: int) -> None:
    if not dpg.does_item_exist(tag):
        return
    dpg.set_value(tag, format_cell_info(cells, width, height, x, y))
