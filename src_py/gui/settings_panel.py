"""Grid size settings panel."""

from __future__ import annotations

import dearpygui.dearpygui as dpg

MIN_GRID_SIZE = 1
MAX_GRID_SIZE = 64

WIDTH_INPUT_TAG = "grid_width_input"
HEIGHT_INPUT_TAG = "grid_height_input"


def build_settings_panel(default_width: int, default_height: int, on_apply) -> None:
    dpg.add_text("Grid Settings")
    dpg.add_input_int(
        label="Width",
        default_value=default_width,
        min_value=MIN_GRID_SIZE,
        max_value=MAX_GRID_SIZE,
        min_clamped=True,
        max_clamped=True,
        tag=WIDTH_INPUT_TAG,
    )
    dpg.add_input_int(
        label="Height",
        default_value=default_height,
        min_value=MIN_GRID_SIZE,
        max_value=MAX_GRID_SIZE,
        min_clamped=True,
        max_clamped=True,
        tag=HEIGHT_INPUT_TAG,
    )
    dpg.add_button(label="Apply", callback=lambda: on_apply())


def read_grid_size() -> tuple[int, int]:
    width = dpg.get_value(WIDTH_INPUT_TAG)
    height = dpg.get_value(HEIGHT_INPUT_TAG)
    width = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, int(width)))
    height = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, int(height)))
    return width, height
