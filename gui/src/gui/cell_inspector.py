"""Hover cell inspector panel."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from wfc_bridge import format_cell_info, worst_case_inspector_body

INSPECTOR_TITLE_HEIGHT = 22
INSPECTOR_LINE_HEIGHT = 20
INSPECTOR_FRAME_PADDING = 28
INSPECTOR_CHAR_WIDTH = 7


def _wrapped_line_count(text: str, wrap_width: int) -> int:
    total = 0
    for line in text.split("\n"):
        line_width = max(len(line), 1) * INSPECTOR_CHAR_WIDTH
        total += max(1, (line_width + wrap_width - 1) // wrap_width)
    return total


def inspector_panel_height(sidebar_width: int = 220) -> int:
    wrap_width = max(sidebar_width - 20, 80)
    body_lines = _wrapped_line_count(worst_case_inspector_body(), wrap_width)
    return INSPECTOR_TITLE_HEIGHT + body_lines * INSPECTOR_LINE_HEIGHT + INSPECTOR_FRAME_PADDING


def update_inspector(tag: str, cells: bytearray, width: int, height: int, x: int, y: int) -> None:
    if not dpg.does_item_exist(tag):
        return
    dpg.set_value(tag, format_cell_info(cells, width, height, x, y))
