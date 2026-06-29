from pathlib import Path

from gui.icon_paths import find_item_icon_path, item_icons_dir


def test_item_icons_dir_exists():
    icons_dir = item_icons_dir()
    assert icons_dir.is_dir()


def test_known_item_icons_exist_and_are_64px():
    from PIL import Image

    for item_id in ("iron-ore", "iron-plate", "transport-belt"):
        path = find_item_icon_path(item_id)
        assert path.parent == item_icons_dir()
        assert path.name == f"{item_id}.jpg"
        with Image.open(path) as image:
            assert image.size == (64, 64)


def test_item_icon_count():
    icons_dir = item_icons_dir()
    jpg_count = len(list(icons_dir.glob("*.jpg")))
    assert jpg_count >= 365
