from pathlib import Path

from gui.belt_textures import (
    ALL_BELT_FLOWS,
    BASE_BELT_FLOWS,
    DEFAULT_FLOW,
    DISPLAY_SIZE,
    FLOW_SPRITE_SPEC,
    FLOW_TO_SPRITE,
    SpriteSpec,
    flow_key,
)
from gui.icon_paths import belt_sprites_dir, find_belt_sprite_path


def test_flow_tag_suffix_has_no_minus_sign():
    from gui.belt_textures import _flow_to_tag_suffix

    assert "-" not in _flow_to_tag_suffix((0, -1, 0, 1))
    assert _flow_to_tag_suffix((0, -1, 0, 1)) == "0_n1_0_1"


def test_flow_key_from_coordinates():
    assert flow_key(0, 1, 0, 0, 0, 2) == (0, -1, 0, 1)


def test_all_valid_belt_flows_have_sprite_spec():
    assert len(FLOW_SPRITE_SPEC) == 12
    assert ALL_BELT_FLOWS == frozenset(FLOW_SPRITE_SPEC)


def test_base_flows_have_unique_sprites():
    assert len(FLOW_TO_SPRITE) == 8
    assert len(set(FLOW_TO_SPRITE.values())) == 8
    assert BASE_BELT_FLOWS == frozenset(FLOW_TO_SPRITE)


def test_default_flow_uses_left_right_sprite():
    assert FLOW_TO_SPRITE[DEFAULT_FLOW] == "left_right"


def test_base_sprite_files_still_eight():
    sprites_dir = belt_sprites_dir()
    assert sprites_dir.is_dir()
    png_files = list(sprites_dir.glob("*_belt.png"))
    assert len(png_files) == 8
    for stem in FLOW_TO_SPRITE.values():
        path = find_belt_sprite_path(stem)
        assert path.parent == sprites_dir
        assert path.name == f"{stem}_belt.png"
        from PIL import Image

        with Image.open(path) as image:
            assert image.size == (64, 64)


def test_load_sprite_image_smoke():
    from gui.belt_textures import _load_sprite_image

    image = _load_sprite_image(SpriteSpec("left_right"))
    assert image.size == (DISPLAY_SIZE, DISPLAY_SIZE)
    extrema = image.getextrema()
    assert extrema[0][1] > 10 or extrema[1][1] > 10


def test_load_mirrored_sprite_image_smoke():
    from gui.belt_textures import _load_sprite_image

    image = _load_sprite_image(SpriteSpec("left_up", flip_v=True))
    assert image.size == (DISPLAY_SIZE, DISPLAY_SIZE)
    extrema = image.getextrema()
    assert extrema[0][1] > 10 or extrema[1][1] > 10
