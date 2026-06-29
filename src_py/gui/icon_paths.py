"""Resolve asset paths for GUI rendering."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

BELT_SPRITES_DIR = "belt_sprites"
ITEM_ICONS_DIR = "icons"


def belt_sprites_dir() -> Path:
    return PROJECT_ROOT / "data" / BELT_SPRITES_DIR


def item_icons_dir() -> Path:
    return PROJECT_ROOT / "data" / ITEM_ICONS_DIR


def find_belt_sprite_path(stem: str) -> Path:
    path = belt_sprites_dir() / f"{stem}_belt.png"
    if path.exists():
        return path
    raise FileNotFoundError(f"Belt sprite not found: {path}")


def find_item_icon_path(item_id: str) -> Path:
    path = item_icons_dir() / f"{item_id}.jpg"
    if path.exists():
        return path
    raise FileNotFoundError(f"Item icon not found: {path}")
