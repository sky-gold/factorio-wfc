"""Static belt textures from PNG sprites in data/belt_sprites/."""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass

import dearpygui.dearpygui as dpg
from PIL import Image

from gui.icon_paths import find_belt_sprite_path

DISPLAY_SIZE = 28

DEFAULT_FLOW = (0, -1, 0, 1)

FlowKey = tuple[int, int, int, int]

# (from_dx, from_dy, to_dx, to_dy) in row/column grid space.
FLOW_TO_SPRITE: dict[FlowKey, str] = {
    (-1, 0, 0, 1): "up_right",
    (0, -1, 0, 1): "left_right",
    (0, 1, 1, 0): "right_down",
    (1, 0, -1, 0): "down_up",
    (-1, 0, 1, 0): "up_down",
    (0, -1, -1, 0): "left_up",
    (0, 1, 0, -1): "right_left",
    (1, 0, 0, -1): "down_left",
}

BASE_BELT_FLOWS: frozenset[FlowKey] = frozenset(FLOW_TO_SPRITE)


@dataclass(frozen=True)
class SpriteSpec:
    stem: str
    flip_h: bool = False
    flip_v: bool = False


# All 12 valid belt flows: 8 base + 4 mirrored corners.
FLOW_SPRITE_SPEC: dict[FlowKey, SpriteSpec] = {
    **{flow: SpriteSpec(stem) for flow, stem in FLOW_TO_SPRITE.items()},
    (-1, 0, 0, -1): SpriteSpec("up_right", flip_h=True),
    (0, -1, 1, 0): SpriteSpec("left_up", flip_v=True),
    (0, 1, -1, 0): SpriteSpec("right_down", flip_v=True),
    (1, 0, 0, 1): SpriteSpec("down_left", flip_h=True),
}

ALL_BELT_FLOWS: frozenset[FlowKey] = frozenset(FLOW_SPRITE_SPEC)

_TEXTURE_TAGS: dict[FlowKey, str | int] = {}
_REGISTERED = False


def flow_key(
    cell_x: int,
    cell_y: int,
    from_x: int,
    from_y: int,
    to_x: int,
    to_y: int,
) -> FlowKey:
    return (from_x - cell_x, from_y - cell_y, to_x - cell_x, to_y - cell_y)


def _flow_to_tag_suffix(flow: FlowKey) -> str:
    def enc(v: int) -> str:
        return f"n{-v}" if v < 0 else str(v)

    return "_".join(enc(v) for v in flow)


def _load_sprite_image(spec: SpriteSpec) -> Image.Image:
    image = Image.open(find_belt_sprite_path(spec.stem)).convert("RGBA")
    if spec.flip_h:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if spec.flip_v:
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if image.size != (64, 64):
        image = image.resize((64, 64), Image.Resampling.LANCZOS)
    return image.resize((DISPLAY_SIZE, DISPLAY_SIZE), Image.Resampling.LANCZOS)


def _register_texture_from_image(tag: str, image: Image.Image) -> None:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        image.save(tmp_path)
        width, height, _, data = dpg.load_image(tmp_path)
        dpg.add_static_texture(width, height, data, tag=tag, parent="icon_registry")
    finally:
        os.unlink(tmp_path)


def register_belt_textures() -> None:
    global _REGISTERED
    if _REGISTERED:
        return

    if not dpg.does_item_exist("icon_registry"):
        dpg.add_texture_registry(tag="icon_registry", show=False)

    for flow, spec in FLOW_SPRITE_SPEC.items():
        image = _load_sprite_image(spec)
        tag = f"belt_tex_{_flow_to_tag_suffix(flow)}"
        _register_texture_from_image(tag, image)
        _TEXTURE_TAGS[flow] = tag

    _REGISTERED = True


def texture_for_belt_tile(
    cell_x: int,
    cell_y: int,
    from_x: int | None = None,
    from_y: int | None = None,
    to_x: int | None = None,
    to_y: int | None = None,
) -> str | int:
    register_belt_textures()

    if from_x is None or to_x is None:
        flow = DEFAULT_FLOW
    else:
        flow = flow_key(cell_x, cell_y, from_x, from_y, to_x, to_y)

    return _TEXTURE_TAGS.get(flow, _TEXTURE_TAGS[DEFAULT_FLOW])
