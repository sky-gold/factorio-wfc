import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gui.grid_canvas import (
    CELL_SIZE,
    GRID_CELLS_TAG,
    build_grid,
    clear_grid,
    refresh_grid,
)
from gui.settings_panel import build_settings_panel, read_grid_size
from gui.tool_panel import ToolState, apply_tool_to_cell, build_cell_params_panel, build_cell_type_panel, refresh_cell_params_panel
from snapshot import create_cells_buffer, set_cell_undecided
from wfc_bridge import ensure_catalog_loaded, validate

DEFAULT_GRID_WIDTH = 10
DEFAULT_GRID_HEIGHT = 20
SIDEBAR_WIDTH = 220


class EditorApp:
    def __init__(self) -> None:
        ensure_catalog_loaded()
        self.grid_width = DEFAULT_GRID_WIDTH
        self.grid_height = DEFAULT_GRID_HEIGHT
        self.cells = create_cells_buffer(self.grid_width, self.grid_height)
        self.tool = ToolState()
        self.cell_tags: list[list[str]] = []

    def _refresh_grid(self) -> None:
        refresh_grid(self.cell_tags, self.cells, self.grid_width, self.grid_height)

    def _on_cell_left_click(self, x: int, y: int) -> None:
        apply_tool_to_cell(self.cells, self.grid_width, x, y, self.tool)
        self._refresh_grid()

    def _on_cell_right_click(self, x: int, y: int) -> None:
        set_cell_undecided(self.cells, self.grid_width, x, y)
        self._refresh_grid()

    def _on_tool_change(self) -> None:
        refresh_cell_params_panel(self.tool)

    def _on_apply_grid_size(self) -> None:
        width, height = read_grid_size()
        if width == self.grid_width and height == self.grid_height:
            return

        self.grid_width = width
        self.grid_height = height
        self.cells = create_cells_buffer(width, height)
        clear_grid(GRID_CELLS_TAG)
        self.cell_tags = build_grid(
            self.cells,
            self.grid_width,
            self.grid_height,
            self._on_cell_left_click,
            self._on_cell_right_click,
        )
        self._update_viewport_size()

    def _on_validate(self) -> None:
        is_valid, message = validate(self.grid_width, self.grid_height, self.cells)
        status = "OK" if is_valid and not message else message or "OK"
        dpg.set_value("status_text", status)

    def _viewport_size(self) -> tuple[int, int]:
        width = min(self.grid_width * CELL_SIZE + SIDEBAR_WIDTH + 80, 1200)
        height = min(self.grid_height * CELL_SIZE + 160, 900)
        return width, height

    def _update_viewport_size(self) -> None:
        width, height = self._viewport_size()
        dpg.set_viewport_width(width)
        dpg.set_viewport_height(height)

    def run(self) -> None:
        dpg.create_context()
        vw, vh = self._viewport_size()
        dpg.create_viewport(title="Factorio WFC", width=vw, height=vh)
        dpg.setup_dearpygui()

        with dpg.window(label="Editor", tag="main_window"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=SIDEBAR_WIDTH, border=True):
                    with dpg.child_window(height=160, border=True):
                        build_settings_panel(
                            self.grid_width,
                            self.grid_height,
                            self._on_apply_grid_size,
                        )

                    dpg.add_spacer(height=4)

                    with dpg.child_window(height=120, border=True):
                        build_cell_type_panel(self.tool, self._on_tool_change)

                    dpg.add_spacer(height=4)

                    with dpg.child_window(height=100, border=True):
                        build_cell_params_panel(self.tool)

                with dpg.child_window(border=True):
                    with dpg.child_window(height=-60, border=True, tag=GRID_CELLS_TAG):
                        self.cell_tags = build_grid(
                            self.cells,
                            self.grid_width,
                            self.grid_height,
                            self._on_cell_left_click,
                            self._on_cell_right_click,
                            parent_tag=GRID_CELLS_TAG,
                        )

                    dpg.add_spacer(height=4)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Validate", callback=lambda: self._on_validate())
                        dpg.add_text("Ready", tag="status_text")

        dpg.set_primary_window("main_window", True)
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()


def main() -> None:
    EditorApp().run()
