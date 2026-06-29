"""Lane icon positions on belt cells relative to flow direction."""

from __future__ import annotations

LANE_ICON_SIZE = 12
CELL_SIZE = 32

FlowKey = tuple[int, int, int, int]
LaneOffset = tuple[int, int]


def _mirror_x(pos: LaneOffset) -> LaneOffset:
    return (CELL_SIZE - LANE_ICON_SIZE - pos[0], pos[1])


def _mirror_y(pos: LaneOffset) -> LaneOffset:
    return (pos[0], CELL_SIZE - LANE_ICON_SIZE - pos[1])


def _mirror_lane_pair(
    left: LaneOffset,
    right: LaneOffset,
    *,
    mirror_x: bool = False,
    mirror_y: bool = False,
) -> tuple[LaneOffset, LaneOffset]:
    if mirror_x:
        left, right = _mirror_x(left), _mirror_x(right)
    if mirror_y:
        left, right = _mirror_y(left), _mirror_y(right)
    return left, right


def _derive_mirrored_lane_offsets(
    base_flow: FlowKey,
    *,
    mirror_x: bool = False,
    mirror_y: bool = False,
) -> tuple[LaneOffset, LaneOffset]:
    """Mirror base lane positions and swap left/right (sprite mirror flips lanes)."""
    left, right = _mirror_lane_pair(
        *_BASE_LANE_OFFSETS[base_flow],
        mirror_x=mirror_x,
        mirror_y=mirror_y,
    )
    return right, left


# (from_dx, from_dy, to_dx, to_dy) -> (left_lane_xy, right_lane_xy) in 32x32 cell space.
_BASE_LANE_OFFSETS: dict[FlowKey, tuple[LaneOffset, LaneOffset]] = {
    # Straights
    (-1, 0, 1, 0): ((10, 1), (10, 19)),
    (1, 0, -1, 0): ((10, 19), (10, 1)),
    (0, -1, 0, 1): ((19, 10), (1, 10)),
    (0, 1, 0, -1): ((1, 10), (19, 10)),
    # Corners (local x grows right, y grows down)
    (0, -1, 1, 0): ((19, 1), (1, 19)),
    (1, 0, 0, 1): ((19, 19), (1, 1)),
    (0, 1, -1, 0): ((1, 19), (19, 1)),
    (-1, 0, 0, -1): ((1, 1), (19, 19)),
}

_DERIVED_LANE_OFFSETS: dict[FlowKey, tuple[LaneOffset, LaneOffset]] = {
    (0, -1, -1, 0): _derive_mirrored_lane_offsets((0, -1, 1, 0), mirror_x=True),
    (-1, 0, 0, 1): _derive_mirrored_lane_offsets((-1, 0, 0, -1), mirror_y=True),
    (1, 0, 0, -1): _derive_mirrored_lane_offsets((1, 0, 0, 1), mirror_y=True),
    (0, 1, 1, 0): _derive_mirrored_lane_offsets((0, 1, -1, 0), mirror_x=True),
}

LANE_OFFSETS: dict[FlowKey, tuple[LaneOffset, LaneOffset]] = {
    **_BASE_LANE_OFFSETS,
    **_DERIVED_LANE_OFFSETS,
}


def lane_icon_positions(flow_key: FlowKey) -> tuple[LaneOffset, LaneOffset] | None:
    return LANE_OFFSETS.get(flow_key)


def mirror_lane_positions_for_flow(
    base_flow: FlowKey,
    *,
    mirror_x: bool = False,
    mirror_y: bool = False,
) -> tuple[LaneOffset, LaneOffset] | None:
    base = _BASE_LANE_OFFSETS.get(base_flow)
    if base is None:
        return None
    return _mirror_lane_pair(*base, mirror_x=mirror_x, mirror_y=mirror_y)
