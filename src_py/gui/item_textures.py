"""Lazy-loaded item icon textures for belt lane overlays."""

from __future__ import annotations

import os
import tempfile

import dearpygui.dearpygui as dpg
from PIL import Image

from gui.belt_lane_layout import LANE_ICON_SIZE
from gui.icon_paths import find_item_icon_path
from snapshot import EMPTY_ITEM_ID
from wfc_bridge import EDITOR_ITEMS

_TEXTURE_TAGS: dict[str, str | int] = {}


def _register_texture_from_image(tag: str, image: Image.Image) -> None:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        image.save(tmp_path)
        width, height, _, data = dpg.load_image(tmp_path)
        if not dpg.does_item_exist("icon_registry"):
            dpg.add_texture_registry(tag="icon_registry", show=False)
        dpg.add_static_texture(width, height, data, tag=tag, parent="icon_registry")
    finally:
        os.unlink(tmp_path)


def texture_for_item_key(item_key: str) -> str | int:
    cached = _TEXTURE_TAGS.get(item_key)
    if cached is not None:
        return cached

    image = Image.open(find_item_icon_path(item_key)).convert("RGBA")
    if image.size != (LANE_ICON_SIZE, LANE_ICON_SIZE):
        image = image.resize((LANE_ICON_SIZE, LANE_ICON_SIZE), Image.Resampling.LANCZOS)

    tag = f"item_tex_{item_key.replace('-', '_')}"
    _register_texture_from_image(tag, image)
    _TEXTURE_TAGS[item_key] = tag
    return tag


def texture_for_item_id(item_id: int) -> str | int | None:
    if item_id == EMPTY_ITEM_ID:
        return None
    if 0 <= item_id < len(EDITOR_ITEMS):
        return texture_for_item_key(EDITOR_ITEMS[item_id])
    return None
