"""2D grid canvas: fixed-size image buttons for all cell types."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Callable

import dearpygui.dearpygui as dpg
from PIL import Image, ImageDraw, ImageFont

from gui.belt_lane_layout import LANE_ICON_SIZE, lane_icon_positions
from gui.belt_textures import flow_key, register_belt_textures, texture_for_belt_tile
from gui.item_textures import texture_for_item_id
from snapshot import (
    EMPTY_ITEM_ID,
    TAG_EMPTY,
    TAG_UNDECIDED,
    TYPE_ID_BELT,
    TYPE_ID_INPUT_BELT,
    TYPE_ID_OUTPUT_BELT,
    get_cell_tag,
    read_cell_belt,
    read_cell_input_belt,
    read_cell_output_belt,
)

CELL_SIZE = 32
CELL_GAP = 2
CELL_PITCH = CELL_SIZE + CELL_GAP
GRID_ORIGIN_X = 8
GRID_CELLS_TAG = "grid_cells_container"
GRID_CANVAS_TAG = "grid_cells_canvas"

CELL_TEX_EMPTY = "cell_tex_empty"
CELL_TEX_UNDECIDED = "cell_tex_undecided"
_GRID_CELL_THEME_TAG = "grid_cell_theme"
_GRID_LAYOUT_THEME_TAG = "grid_layout_theme"

_CELL_TEXTURES_READY = False


@dataclass
class GridViewState:
    hover_x: int = -1
    hover_y: int = -1


def _make_label_texture_image(label: str) -> Image.Image:
    image = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (48, 48, 48, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((CELL_SIZE - text_w) // 2, (CELL_SIZE - text_h) // 2),
        label,
        fill=(220, 220, 220, 255),
        font=font,
    )
    return image


def _register_static_texture(tag: str, image: Image.Image) -> None:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        image.save(tmp_path)
        width, height, _, data = dpg.load_image(tmp_path)
        dpg.add_static_texture(width, height, data, tag=tag, parent="icon_registry")
    finally:
        os.unlink(tmp_path)


def _ensure_grid_cell_theme() -> None:
    if dpg.does_item_exist(_GRID_CELL_THEME_TAG):
        return
    with dpg.theme(tag=_GRID_CELL_THEME_TAG):
        with dpg.theme_component(dpg.mvImageButton):
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)


def _ensure_grid_layout_theme() -> None:
    if dpg.does_item_exist(_GRID_LAYOUT_THEME_TAG):
        return
    with dpg.theme(tag=_GRID_LAYOUT_THEME_TAG):
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)


def _ensure_cell_textures() -> None:
    global _CELL_TEXTURES_READY
    if _CELL_TEXTURES_READY:
        return

    register_belt_textures()
    _register_static_texture(CELL_TEX_EMPTY, _make_label_texture_image("."))
    _register_static_texture(CELL_TEX_UNDECIDED, _make_label_texture_image("?"))
    _ensure_grid_cell_theme()
    _ensure_grid_layout_theme()
    _CELL_TEXTURES_READY = True


def _safe_rect_min(tag: str) -> tuple[float, float] | None:
    if not dpg.does_item_exist(tag):
        return None
    try:
        ox, oy = dpg.get_item_rect_min(tag)
        return float(ox), float(oy)
    except KeyError:
        state = dpg.get_item_state(tag)
        rect = state.get("rect_min")
        if rect is not None:
            return float(rect[0]), float(rect[1])
    return None


def grid_pixel_extent(cell_count: int) -> int:
    if cell_count <= 0:
        return 0
    return cell_count * CELL_SIZE + (cell_count - 1) * CELL_GAP


def screen_to_cell(
    mx: float,
    my: float,
    width: int,
    height: int,
    anchor_tag: str = "cell_0_0",
) -> tuple[int, int]:
    anchor = _safe_rect_min(anchor_tag)
    if anchor is None:
        return -1, -1
    origin_x, origin_y = anchor
    rel_x = mx - origin_x
    rel_y = my - origin_y
    if rel_x < 0 or rel_y < 0:
        return -1, -1

    x = int(rel_y // CELL_PITCH)
    y = int(rel_x // CELL_PITCH)
    if x < 0 or y < 0 or x >= height or y >= width:
        return -1, -1

    if rel_x - y * CELL_PITCH >= CELL_SIZE or rel_y - x * CELL_PITCH >= CELL_SIZE:
        return -1, -1
    return x, y


def _cell_texture(cells: bytearray, width: int, x: int, y: int) -> str | int:
    tag = get_cell_tag(cells, width, x, y)
    if tag == TYPE_ID_BELT:
        belt = read_cell_belt(cells, width, x, y)
        if belt is not None:
            return texture_for_belt_tile(x, y, belt.from_x, belt.from_y, belt.to_x, belt.to_y)
        return CELL_TEX_UNDECIDED
    if tag == TYPE_ID_INPUT_BELT:
        input_belt = read_cell_input_belt(cells, width, x, y)
        if input_belt is not None:
            from_x = 2 * x - input_belt.to_x
            from_y = 2 * y - input_belt.to_y
            return texture_for_belt_tile(x, y, from_x, from_y, input_belt.to_x, input_belt.to_y)
        return CELL_TEX_UNDECIDED
    if tag == TYPE_ID_OUTPUT_BELT:
        output_belt = read_cell_output_belt(cells, width, x, y)
        if output_belt is not None:
            to_x = 2 * x - output_belt.from_x
            to_y = 2 * y - output_belt.from_y
            return texture_for_belt_tile(x, y, output_belt.from_x, output_belt.from_y, to_x, to_y)
        return CELL_TEX_UNDECIDED
    if tag == TAG_EMPTY:
        return CELL_TEX_EMPTY
    return CELL_TEX_UNDECIDED


def _add_cell_button(
    tag: str,
    texture: str | int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None,
    x: int,
    y: int,
    *,
    parent: str | int,
) -> None:
    dpg.add_image_button(
        texture,
        width=CELL_SIZE,
        height=CELL_SIZE,
        frame_padding=0,
        tag=tag,
        parent=parent,
        pos=(y * CELL_PITCH, x * CELL_PITCH),
        callback=lambda s, a, *_, cx=x, cy=y: on_left_click(cx, cy),
    )
    dpg.bind_item_theme(tag, _GRID_CELL_THEME_TAG)

    with dpg.item_handler_registry() as handler:
        dpg.add_item_clicked_handler(
            button=dpg.mvMouseButton_Right,
            callback=lambda s, a, *_, cx=x, cy=y: on_right_click(cx, cy),
        )
        if on_hover is not None:
            dpg.add_item_hover_handler(
                callback=lambda s, a, *_, cx=x, cy=y: on_hover(cx, cy) if a else None,
            )
    dpg.bind_item_handler_registry(tag, handler)


def _add_lane_overlay(
    texture: str | int,
    cell_x: int,
    cell_y: int,
    offset_x: int,
    offset_y: int,
    *,
    parent: str | int,
) -> None:
    # Screen pos matches _add_cell_button: column -> X, row -> Y.
    dpg.add_image(
        texture,
        width=LANE_ICON_SIZE,
        height=LANE_ICON_SIZE,
        parent=parent,
        pos=(cell_y * CELL_PITCH + offset_x, cell_x * CELL_PITCH + offset_y),
    )


def _add_rate_lane_overlay(
    texture: str | int,
    rate: float,
    cell_x: int,
    cell_y: int,
    offset_x: int,
    offset_y: int,
    *,
    parent: str | int,
) -> None:
    base_x = cell_y * CELL_PITCH + max(0, offset_x - 14)
    base_y = cell_x * CELL_PITCH + max(0, offset_y - 1)
    dpg.add_text(f"{rate:.1f}", parent=parent, pos=(base_x, base_y))
    dpg.add_image(
        texture,
        width=LANE_ICON_SIZE,
        height=LANE_ICON_SIZE,
        parent=parent,
        pos=(base_x + 22, base_y),
    )


def _add_belt_cell(
    tag: str,
    cells: bytearray,
    grid_width: int,
    cell_x: int,
    cell_y: int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None,
    *,
    parent: str | int,
) -> None:
    belt = read_cell_belt(cells, grid_width, cell_x, cell_y)
    if belt is None:
        _add_cell_button(
            tag,
            CELL_TEX_UNDECIDED,
            on_left_click,
            on_right_click,
            on_hover,
            cell_x,
            cell_y,
            parent=parent,
        )
        return

    belt_tex = texture_for_belt_tile(
        cell_x, cell_y, belt.from_x, belt.from_y, belt.to_x, belt.to_y
    )
    _add_cell_button(
        tag,
        belt_tex,
        on_left_click,
        on_right_click,
        on_hover,
        cell_x,
        cell_y,
        parent=parent,
    )

    flow = flow_key(cell_x, cell_y, belt.from_x, belt.from_y, belt.to_x, belt.to_y)
    positions = lane_icon_positions(flow)
    if positions is None:
        return

    left_pos, right_pos = positions
    if belt.left_item_id != EMPTY_ITEM_ID:
        left_tex = texture_for_item_id(belt.left_item_id)
        if left_tex is not None:
            _add_lane_overlay(left_tex, cell_x, cell_y, left_pos[0], left_pos[1], parent=parent)
    if belt.right_item_id != EMPTY_ITEM_ID:
        right_tex = texture_for_item_id(belt.right_item_id)
        if right_tex is not None:
            _add_lane_overlay(right_tex, cell_x, cell_y, right_pos[0], right_pos[1], parent=parent)


def _add_input_belt_cell(
    tag: str,
    cells: bytearray,
    grid_width: int,
    cell_x: int,
    cell_y: int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None,
    *,
    parent: str | int,
) -> None:
    input_belt = read_cell_input_belt(cells, grid_width, cell_x, cell_y)
    if input_belt is None:
        _add_cell_button(
            tag,
            CELL_TEX_UNDECIDED,
            on_left_click,
            on_right_click,
            on_hover,
            cell_x,
            cell_y,
            parent=parent,
        )
        return

    from_x = 2 * cell_x - input_belt.to_x
    from_y = 2 * cell_y - input_belt.to_y
    belt_tex = texture_for_belt_tile(cell_x, cell_y, from_x, from_y, input_belt.to_x, input_belt.to_y)
    _add_cell_button(tag, belt_tex, on_left_click, on_right_click, on_hover, cell_x, cell_y, parent=parent)

    flow = flow_key(cell_x, cell_y, from_x, from_y, input_belt.to_x, input_belt.to_y)
    positions = lane_icon_positions(flow)
    if positions is None:
        return

    left_pos, right_pos = positions
    if input_belt.left_item_id != EMPTY_ITEM_ID:
        left_tex = texture_for_item_id(input_belt.left_item_id)
        if left_tex is not None:
            _add_rate_lane_overlay(
                left_tex, input_belt.left_max_rate, cell_x, cell_y, left_pos[0], left_pos[1], parent=parent
            )
    if input_belt.right_item_id != EMPTY_ITEM_ID:
        right_tex = texture_for_item_id(input_belt.right_item_id)
        if right_tex is not None:
            _add_rate_lane_overlay(
                right_tex, input_belt.right_max_rate, cell_x, cell_y, right_pos[0], right_pos[1], parent=parent
            )


def _add_output_belt_cell(
    tag: str,
    cells: bytearray,
    grid_width: int,
    cell_x: int,
    cell_y: int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None,
    *,
    parent: str | int,
) -> None:
    output_belt = read_cell_output_belt(cells, grid_width, cell_x, cell_y)
    if output_belt is None:
        _add_cell_button(
            tag,
            CELL_TEX_UNDECIDED,
            on_left_click,
            on_right_click,
            on_hover,
            cell_x,
            cell_y,
            parent=parent,
        )
        return

    to_x = 2 * cell_x - output_belt.from_x
    to_y = 2 * cell_y - output_belt.from_y
    belt_tex = texture_for_belt_tile(cell_x, cell_y, output_belt.from_x, output_belt.from_y, to_x, to_y)
    _add_cell_button(tag, belt_tex, on_left_click, on_right_click, on_hover, cell_x, cell_y, parent=parent)

    flow = flow_key(cell_x, cell_y, output_belt.from_x, output_belt.from_y, to_x, to_y)
    positions = lane_icon_positions(flow)
    if positions is None:
        return

    left_pos, right_pos = positions
    if output_belt.left_item_id != EMPTY_ITEM_ID:
        left_tex = texture_for_item_id(output_belt.left_item_id)
        if left_tex is not None:
            _add_rate_lane_overlay(
                left_tex, output_belt.left_min_rate, cell_x, cell_y, left_pos[0], left_pos[1], parent=parent
            )
    if output_belt.right_item_id != EMPTY_ITEM_ID:
        right_tex = texture_for_item_id(output_belt.right_item_id)
        if right_tex is not None:
            _add_rate_lane_overlay(
                right_tex, output_belt.right_min_rate, cell_x, cell_y, right_pos[0], right_pos[1], parent=parent
            )


def clear_grid(parent_tag: str = GRID_CELLS_TAG) -> None:
    if dpg.does_item_exist(parent_tag):
        dpg.delete_item(parent_tag, children_only=True)


def build_grid(
    cells: bytearray,
    width: int,
    height: int,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None = None,
    parent_tag: str = GRID_CELLS_TAG,
) -> list[list[str]]:
    _ensure_cell_textures()

    canvas_w = grid_pixel_extent(width)
    canvas_h = grid_pixel_extent(height)
    dpg.add_child_window(
        width=canvas_w,
        height=canvas_h,
        border=False,
        no_scrollbar=True,
        tag=GRID_CANVAS_TAG,
        parent=parent_tag,
    )
    dpg.bind_item_theme(GRID_CANVAS_TAG, _GRID_LAYOUT_THEME_TAG)

    cell_tags: list[list[str]] = []
    for x in range(height):
        row: list[str] = []
        for y in range(width):
            tag = f"cell_{x}_{y}"
            cell_tag = get_cell_tag(cells, width, x, y)
            if cell_tag == TYPE_ID_BELT:
                _add_belt_cell(
                    tag,
                    cells,
                    width,
                    x,
                    y,
                    on_left_click,
                    on_right_click,
                    on_hover,
                    parent=GRID_CANVAS_TAG,
                )
            elif cell_tag == TYPE_ID_INPUT_BELT:
                _add_input_belt_cell(
                    tag,
                    cells,
                    width,
                    x,
                    y,
                    on_left_click,
                    on_right_click,
                    on_hover,
                    parent=GRID_CANVAS_TAG,
                )
            elif cell_tag == TYPE_ID_OUTPUT_BELT:
                _add_output_belt_cell(
                    tag,
                    cells,
                    width,
                    x,
                    y,
                    on_left_click,
                    on_right_click,
                    on_hover,
                    parent=GRID_CANVAS_TAG,
                )
            else:
                tex = _cell_texture(cells, width, x, y)
                _add_cell_button(
                    tag,
                    tex,
                    on_left_click,
                    on_right_click,
                    on_hover,
                    x,
                    y,
                    parent=GRID_CANVAS_TAG,
                )
            row.append(tag)
        cell_tags.append(row)
    return cell_tags


def refresh_grid(
    cell_tags: list[list[str]],
    cells: bytearray,
    width: int,
    height: int,
    state: GridViewState,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    on_hover: Callable[[int, int], None] | None = None,
    parent_tag: str = GRID_CELLS_TAG,
) -> list[list[str]]:
    del cell_tags, state
    clear_grid(parent_tag)
    return build_grid(cells, width, height, on_left_click, on_right_click, on_hover, parent_tag)


def draw_grid(
    cells: bytearray,
    width: int,
    height: int,
    state: GridViewState,
    on_left_click: Callable[[int, int], None],
    on_right_click: Callable[[int, int], None],
    draw_tag: str = "grid_draw",
    parent_tag: str | None = None,
) -> list[list[str]]:
    del draw_tag, state
    parent = parent_tag or GRID_CELLS_TAG
    clear_grid(parent)
    return build_grid(cells, width, height, on_left_click, on_right_click, parent)


def cell_in_bounds(x: int, y: int, width: int, height: int) -> bool:
    return 0 <= x < height and 0 <= y < width
