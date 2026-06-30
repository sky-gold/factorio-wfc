from gui.belt_lane_layout import (
    LANE_OFFSETS,
    lane_icon_positions,
    mirror_lane_positions_for_flow,
)
from gui.belt_textures import ALL_BELT_FLOWS
from gui.icon_paths import find_item_icon_path
from wfc_bridge import EDITOR_ITEMS


def test_all_belt_flows_have_lane_offsets():
    assert len(ALL_BELT_FLOWS) == 12
    for flow in ALL_BELT_FLOWS:
        assert flow in LANE_OFFSETS
        assert lane_icon_positions(flow) is not None


def test_left_right_horizontal_lane_order():
    left_right = (0, -1, 0, 1)
    right_left = (0, 1, 0, -1)
    lr_left, lr_right = lane_icon_positions(left_right)
    rl_left, rl_right = lane_icon_positions(right_left)
    assert lr_left[1] < lr_right[1]
    assert rl_left[1] > rl_right[1]


def test_corner_lane_corners_match_flow():
    assert lane_icon_positions((0, -1, -1, 0)) == ((1, 1), (19, 19))
    assert lane_icon_positions((1, 0, 0, -1)) == ((1, 19), (19, 1))
    assert lane_icon_positions((1, 0, 0, 1)) == ((1, 1), (19, 19))
    assert lane_icon_positions((-1, 0, 0, 1)) == ((19, 1), (1, 19))
    assert lane_icon_positions((-1, 0, 0, -1)) == ((19, 19), (1, 1))


def test_derived_corner_lanes_swap_after_mirror():
    left_up = (0, -1, -1, 0)
    left_down = (-1, 0, 0, 1)
    mirrored = mirror_lane_positions_for_flow(left_up, mirror_y=True)
    assert mirrored is not None
    left_pos, right_pos = mirrored
    assert lane_icon_positions(left_down) == (right_pos, left_pos)


def test_editor_items_map_to_icon_files():
    for item_key in EDITOR_ITEMS:
        path = find_item_icon_path(item_key)
        assert path.name == f"{item_key}.jpg"
