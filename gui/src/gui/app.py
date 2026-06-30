import logging
import sys
from pathlib import Path

import dearpygui.dearpygui as dpg

log = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gui.belt_textures import register_belt_textures
from gui.cell_inspector import inspector_panel_height, update_inspector
from gui.grid_canvas import (
    GRID_CELLS_TAG,
    GRID_ORIGIN_X,
    GridViewState,
    build_grid,
    cell_in_bounds,
    clear_grid,
    draw_grid,
    grid_pixel_extent,
    refresh_grid,
    screen_to_cell,
)
from gui.settings_panel import build_settings_panel, read_grid_size
from gui.tool_panel import ToolState, apply_tool_to_cell, build_cell_params_panel, build_cell_type_panel, refresh_cell_params_panel
from snapshot import create_cells_buffer, export_grid_json, set_cell_undecided
from wfc_bridge import ensure_catalog_loaded, item_key_to_id, item_label, validate

DEFAULT_GRID_WIDTH = 10
DEFAULT_GRID_HEIGHT = 10
SIDEBAR_WIDTH = 220
PANEL_SETTINGS_HEIGHT = 160
PANEL_CELL_TYPE_HEIGHT = 140
PANEL_CELL_PARAMS_HEIGHT = 430
PANEL_SPACER = 4
GRID_FOOTER_HEIGHT = PANEL_SPACER + 28  # spacer + Validate/Export row
VIEWPORT_PADDING = 48
VIEWPORT_MAX_HEIGHT = 1200
INSPECTOR_TAG = "inspector_text"


def sidebar_content_height() -> int:
    return (
        PANEL_SETTINGS_HEIGHT
        + PANEL_SPACER
        + PANEL_CELL_TYPE_HEIGHT
        + PANEL_SPACER
        + PANEL_CELL_PARAMS_HEIGHT
        + PANEL_SPACER
        + inspector_panel_height(SIDEBAR_WIDTH)
    )


class EditorApp:
    def __init__(self) -> None:
        log.info("EditorApp.__init__ start")
        ensure_catalog_loaded()
        self.grid_width = DEFAULT_GRID_WIDTH
        self.grid_height = DEFAULT_GRID_HEIGHT
        self.cells = create_cells_buffer(self.grid_width, self.grid_height)
        self.tool = ToolState()
        self.view = GridViewState()
        self.cell_tags: list[list[str]] = []
        log.info(
            "EditorApp ready (grid %sx%s = %s cols x %s rows)",
            self.grid_width,
            self.grid_height,
            self.grid_width,
            self.grid_height,
        )

    def _on_cell_hover(self, x: int, y: int) -> None:
        if x == self.view.hover_x and y == self.view.hover_y:
            return
        self.view.hover_x = x
        self.view.hover_y = y
        self._update_inspector()

    def _clear_hover(self) -> None:
        hx, hy = self.view.hover_x, self.view.hover_y
        if (hx is None or hx < 0) and (hy is None or hy < 0):
            return
        self.view.hover_x = -1
        self.view.hover_y = -1
        self._update_inspector()

    def _refresh_grid(self) -> None:
        self.cell_tags = refresh_grid(
            self.cell_tags,
            self.cells,
            self.grid_width,
            self.grid_height,
            self.view,
            self._on_cell_left_click,
            self._on_cell_right_click,
            self._on_cell_hover,
            parent_tag=GRID_CELLS_TAG,
        )

    def _update_inspector(self) -> None:
        update_inspector(
            INSPECTOR_TAG,
            self.cells,
            self.grid_width,
            self.grid_height,
            self.view.hover_x,
            self.view.hover_y,
        )

    def _on_cell_left_click(self, x: int, y: int) -> None:
        if not cell_in_bounds(x, y, self.grid_width, self.grid_height):
            return
        apply_tool_to_cell(self.cells, self.grid_width, x, y, self.tool)
        self._refresh_grid()
        self._update_inspector()

    def _on_cell_right_click(self, x: int, y: int) -> None:
        if not cell_in_bounds(x, y, self.grid_width, self.grid_height):
            return
        set_cell_undecided(self.cells, self.grid_width, x, y)
        self._refresh_grid()
        self._update_inspector()

    def _on_mouse_move(self, sender, app_data) -> None:
        mx, my = dpg.get_mouse_pos(local=False)
        x, y = screen_to_cell(mx, my, self.grid_width, self.grid_height)
        if x < 0 or y < 0:
            self._clear_hover()

    def _on_tool_change(self) -> None:
        refresh_cell_params_panel(self.tool)

    def _on_apply_grid_size(self) -> None:
        width, height = read_grid_size()
        if width == self.grid_width and height == self.grid_height:
            return

        self.grid_width = width
        self.grid_height = height
        self.cells = create_cells_buffer(width, height)
        self.view.hover_x = -1
        self.view.hover_y = -1
        clear_grid(GRID_CELLS_TAG)
        self.cell_tags = build_grid(
            self.cells,
            self.grid_width,
            self.grid_height,
            self._on_cell_left_click,
            self._on_cell_right_click,
            self._on_cell_hover,
            parent_tag=GRID_CELLS_TAG,
        )
        self._update_inspector()
        self._update_viewport_size()

    def _on_validate(self) -> None:
        log.info("Validate clicked (grid %sx%s)", self.grid_width, self.grid_height)
        is_valid, message = validate(self.grid_width, self.grid_height, self.cells)
        log.info("Validate result: is_valid=%s message=%r", is_valid, message)
        status = "OK" if is_valid and not message else message or "OK"
        dpg.set_value("status_text", status)

    def _on_export(self) -> None:
        text = export_grid_json(
            self.grid_width,
            self.grid_height,
            self.cells,
            item_label_fn=item_label,
        )
        dpg.set_clipboard_text(text)
        log.info("Export copied to clipboard (%s chars, grid %sx%s)", len(text), self.grid_width, self.grid_height)
        dpg.set_value("status_text", f"Copied to clipboard ({len(text)} chars)")

    def _viewport_size(self) -> tuple[int, int]:
        grid_w = grid_pixel_extent(self.grid_width) + GRID_ORIGIN_X + 40
        width = min(grid_w + SIDEBAR_WIDTH + VIEWPORT_PADDING, 1200)
        grid_h = grid_pixel_extent(self.grid_height) + GRID_FOOTER_HEIGHT
        content_h = max(sidebar_content_height(), grid_h)
        height = min(content_h + VIEWPORT_PADDING, VIEWPORT_MAX_HEIGHT)
        return width, height

    def _update_viewport_size(self) -> None:
        width, height = self._viewport_size()
        dpg.set_viewport_width(width)
        dpg.set_viewport_height(height)

    def run(self) -> None:
        log.info("Dear PyGui: create_context")
        dpg.create_context()
        vw, vh = self._viewport_size()
        log.info("Dear PyGui: create_viewport %sx%s", vw, vh)
        dpg.create_viewport(title="Factorio WFC", width=vw, height=vh)
        dpg.setup_dearpygui()

        log.info("Registering belt textures ...")
        register_belt_textures()
        log.info("Belt textures OK")

        with dpg.handler_registry(tag="global_handlers"):
            dpg.add_mouse_move_handler(callback=self._on_mouse_move)

        with dpg.window(label="Editor", tag="main_window"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=SIDEBAR_WIDTH, border=True):
                    with dpg.child_window(height=PANEL_SETTINGS_HEIGHT, border=True):
                        build_settings_panel(
                            self.grid_width,
                            self.grid_height,
                            self._on_apply_grid_size,
                        )

                    dpg.add_spacer(height=PANEL_SPACER)

                    with dpg.child_window(height=PANEL_CELL_TYPE_HEIGHT, border=True):
                        build_cell_type_panel(self.tool, self._on_tool_change)

                    dpg.add_spacer(height=PANEL_SPACER)

                    with dpg.child_window(height=PANEL_CELL_PARAMS_HEIGHT, border=True):
                        build_cell_params_panel(self.tool)

                    dpg.add_spacer(height=PANEL_SPACER)

                    with dpg.child_window(height=inspector_panel_height(SIDEBAR_WIDTH), border=True):
                        dpg.add_text("Inspector")
                        dpg.add_text("No cell", tag=INSPECTOR_TAG, wrap=SIDEBAR_WIDTH - 20)

                with dpg.group():
                    with dpg.group(tag=GRID_CELLS_TAG):
                        self.cell_tags = build_grid(
                            self.cells,
                            self.grid_width,
                            self.grid_height,
                            self._on_cell_left_click,
                            self._on_cell_right_click,
                            self._on_cell_hover,
                            parent_tag=GRID_CELLS_TAG,
                        )

                    dpg.add_spacer(height=PANEL_SPACER)
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Validate", callback=lambda: self._on_validate())
                        dpg.add_button(label="Export", callback=lambda: self._on_export())
                        dpg.add_text("Ready", tag="status_text")

        dpg.set_primary_window("main_window", True)
        log.info("Dear PyGui: show_viewport")
        dpg.show_viewport()
        log.info("Dear PyGui: start_dearpygui (blocking until window closes)")
        dpg.start_dearpygui()
        log.info("Dear PyGui: destroy_context")
        dpg.destroy_context()


def main() -> None:
    log.info("gui.app.main() creating EditorApp")
    EditorApp().run()
    log.info("gui.app.main() done")
