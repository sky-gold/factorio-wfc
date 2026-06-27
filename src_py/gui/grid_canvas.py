"""2D grid canvas: build, refresh, mouse handlers."""

from __future__ import annotations

from typing import Callable

import dearpygui.dearpygui as dpg

from snapshot import is_cell_undecided

CELL_SIZE = 28
GRID_CELLS_TAG = "grid_cells_container"


def cell_label(cells: bytearray, width: int, x: int, y: int) -> str:
    return "?" if is_cell_undecided(cells, width, x, y) else "."


def refresh_grid(cell_tags: list[list[str]], cells: bytearray, width: int, height: int) -> None:
    for y in range(height):
        for x in range(width):
            dpg.configure_item(cell_tags[y][x], label=cell_label(cells, width, x, y))


def clear_grid(parent_tag: str = GRID_CELLS_TAG) -> None:
    if dpg.does_item_exist(parent_tag):
        dpg.delete_item(parent_tag, children_only=True)


def build_grid(
    cells: bytearray,
    width: int,
    height: int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    parent_tag: str = GRID_CELLS_TAG,
) -> list[list[str]]:
    cell_tags: list[list[str]] = []
    for y in range(height):
        row: list[str] = []
        with dpg.group(parent=parent_tag):
            with dpg.group(horizontal=True):
                for x in range(width):
                    tag = f"cell_{x}_{y}"
                    dpg.add_button(
                        label=cell_label(cells, width, x, y),
                        width=CELL_SIZE,
                        height=CELL_SIZE,
                        tag=tag,
                        callback=_make_left_callback(on_left_click, x, y),
                    )
                    with dpg.item_handler_registry() as handler:
                        dpg.add_item_clicked_handler(
                            button=dpg.mvMouseButton_Right,
                            callback=_make_right_callback(on_right_click, x, y),
                        )
                    dpg.bind_item_handler_registry(tag, handler)
                    row.append(tag)
        cell_tags.append(row)
    return cell_tags


def _make_left_callback(callback: Callable[[int, int], None], x: int, y: int):
    def _handler(sender, app_data) -> None:
        callback(x, y)

    return _handler


def _make_right_callback(callback: Callable[[int, int], None], x: int, y: int):
    def _handler(sender, app_data) -> None:
        callback(x, y)

    return _handler
