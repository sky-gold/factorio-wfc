#include "rules/belt_rules.h"

#include "cell.h"
#include "grid.h"
#include "rules/belt_flow.h"
#include "rules/rule_result.h"
#include "tile.h"

#include <format>
#include <optional>
#include <string>
#include <string_view>

namespace fwfc {

namespace {

struct LaneInputState {
    bool left = false;
    bool right = false;
};

enum class LaneSide {
    Left,
    Right,
};

ItemId lane_item(const BeltTile& belt, LaneSide side) {
    return side == LaneSide::Left ? belt.left_item_id : belt.right_item_id;
}

std::string_view lane_name(LaneSide side) {
    return side == LaneSide::Left ? "left" : "right";
}

ValidationResult check_resource_feeds_into_lane(const BeltTile& belt, LaneSide side, Cell cell, Cell feeder_cell,
                                                ItemId item_id) {
    if (item_id == kEmptyItemId) {
        return rules_detail::valid();
    }
    const ItemId expected_item = lane_item(belt, side);
    if (item_id != expected_item) {
        return rules_detail::invalid(std::format(
            "Trying to feed item {0} into {1} lane at {2} from {3}, but expected item is {4}", item_id,
            lane_name(side), cell, feeder_cell, expected_item));
    }
    return rules_detail::valid();
}

ValidationResult check_feeder_belt_into_cell(const Grid& grid, Cell cell, Cell feeder_cell,
                                             const BeltTile& center_belt, LaneInputState& lanes) {
    if (!grid.in_bounds(feeder_cell)) {
        return rules_detail::valid();
    }
    const std::optional<Tile> feeder_tile =
        grid.get(static_cast<std::size_t>(feeder_cell.x), static_cast<std::size_t>(feeder_cell.y));
    if (!feeder_tile.has_value()) {
        lanes.left = true;
        lanes.right = true;
        return rules_detail::valid();
    }

    const std::optional<rules_detail::BeltLaneItems> feeder_lanes =
        rules_detail::outgoing_lane_items_to_cell(feeder_cell, cell, feeder_tile.value());
    if (!feeder_lanes.has_value()) {
        return rules_detail::valid();
    }
    if (feeder_lanes.value().left_item_id != kEmptyItemId) {
        lanes.left = true;
    }
    if (feeder_lanes.value().right_item_id != kEmptyItemId) {
        lanes.right = true;
    }
    ValidationResult result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Left, cell, feeder_cell,
                                       feeder_lanes.value().left_item_id);
    if (!result.is_valid) {
        return result;
    }
    result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Right, cell, feeder_cell,
                                       feeder_lanes.value().right_item_id);
    if (!result.is_valid) {
        return result;
    }
    return rules_detail::valid();
}

ValidationResult check_left_side_feeder_belt_into_cell(const Grid& grid, Cell cell, Cell feeder_cell,
                                                       const BeltTile& center_belt, LaneInputState& lanes) {
    if (!grid.in_bounds(feeder_cell)) {
        return rules_detail::valid();
    }
    const std::optional<Tile> feeder_tile =
        grid.get(static_cast<std::size_t>(feeder_cell.x), static_cast<std::size_t>(feeder_cell.y));
    if (!feeder_tile.has_value()) {
        lanes.left = true;
        return rules_detail::valid();
    }

    const std::optional<rules_detail::BeltLaneItems> feeder_lanes =
        rules_detail::outgoing_lane_items_to_cell(feeder_cell, cell, feeder_tile.value());
    if (!feeder_lanes.has_value()) {
        return rules_detail::valid();
    }
    if (feeder_lanes.value().left_item_id != kEmptyItemId) {
        lanes.left = true;
    }
    if (feeder_lanes.value().right_item_id != kEmptyItemId) {
        lanes.left = true;
    }
    ValidationResult result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Left, cell, feeder_cell,
                                       feeder_lanes.value().left_item_id);
    if (!result.is_valid) {
        return result;
    }
    result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Left, cell, feeder_cell,
                                       feeder_lanes.value().right_item_id);
    if (!result.is_valid) {
        return result;
    }
    return rules_detail::valid();
}

ValidationResult check_right_side_feeder_belt_into_cell(const Grid& grid, Cell cell, Cell feeder_cell,
                                                        const BeltTile& center_belt, LaneInputState& lanes) {
    if (!grid.in_bounds(feeder_cell)) {
        return rules_detail::valid();
    }
    const std::optional<Tile> feeder_tile =
        grid.get(static_cast<std::size_t>(feeder_cell.x), static_cast<std::size_t>(feeder_cell.y));
    if (!feeder_tile.has_value()) {
        lanes.right = true;
        return rules_detail::valid();
    }

    const std::optional<rules_detail::BeltLaneItems> feeder_lanes =
        rules_detail::outgoing_lane_items_to_cell(feeder_cell, cell, feeder_tile.value());
    if (!feeder_lanes.has_value()) {
        return rules_detail::valid();
    }
    if (feeder_lanes.value().left_item_id != kEmptyItemId) {
        lanes.right = true;
    }
    if (feeder_lanes.value().right_item_id != kEmptyItemId) {
        lanes.right = true;
    }
    ValidationResult result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Right, cell, feeder_cell,
                                       feeder_lanes.value().left_item_id);
    if (!result.is_valid) {
        return result;
    }
    result =
        check_resource_feeds_into_lane(center_belt, LaneSide::Right, cell, feeder_cell,
                                       feeder_lanes.value().right_item_id);
    if (!result.is_valid) {
        return result;
    }
    return rules_detail::valid();
}

TriState cell_feeds_into_cell_tristate(const Grid& grid, Cell feeder, Cell cell) {
    if (!grid.in_bounds(feeder)) {
        return TriState::False;
    }
    const std::optional<Tile> feeder_tile =
        grid.get(static_cast<std::size_t>(feeder.x), static_cast<std::size_t>(feeder.y));

    if (!feeder_tile.has_value()) {
        return TriState::Unknown;
    }
    return rules_detail::outgoing_lane_items_to_cell(feeder, cell, feeder_tile.value()).has_value() ? TriState::True
                                                                                                    : TriState::False;
}

ValidationResult check_belt_resources(const Grid& grid, Cell cell, Cell from, Cell to, const BeltTile& belt) {
    LaneInputState lanes;
    const auto [left_side_cell, right_side_cell] = belt_side_cells(cell, belt);

    ValidationResult result = check_feeder_belt_into_cell(grid, cell, from, belt, lanes);
    if (!result.is_valid) {
        return result;
    }

    if (!cells_are_curve_neighbors(cell, from, to)) {
        result = check_left_side_feeder_belt_into_cell(grid, cell, left_side_cell, belt, lanes);
        if (!result.is_valid) {
            return result;
        }
        result = check_right_side_feeder_belt_into_cell(grid, cell, right_side_cell, belt, lanes);
        if (!result.is_valid) {
            return result;
        }
    }

    if (!lanes.left && belt.left_item_id != kEmptyItemId) {
        return rules_detail::invalid(std::format("Expected item {0} on left lane at {1}, but no input on left side",
                                                 belt.left_item_id, cell));
    }
    if (!lanes.right && belt.right_item_id != kEmptyItemId) {
        return rules_detail::invalid(std::format("Expected item {0} on right lane at {1}, but no input on right side",
                                                 belt.right_item_id, cell));
    }

    return rules_detail::valid();
}

ValidationResult check_belt_topology(const Grid& grid, Cell cell, Cell from, Cell to, const BeltTile& belt) {
    const auto [left_side_cell, right_side_cell] = belt_side_cells(cell, belt);
    const TriState left_feeds = cell_feeds_into_cell_tristate(grid, left_side_cell, cell);
    const TriState right_feeds = cell_feeds_into_cell_tristate(grid, right_side_cell, cell);
    const TriState from_feeds = cell_feeds_into_cell_tristate(grid, from, cell);
    if (cells_are_curve_neighbors(cell, from, to)) {
        if (from_feeds == TriState::False) {
            return rules_detail::invalid(
                std::format("Curve belt requires flow from from_cell, but it is not fed from {0}", from));
        }
        if (left_feeds == TriState::True) {
            return rules_detail::invalid(
                std::format("Curve belt cannot accept left side feeder, but it is fed from {0}", left_side_cell));
        }
        if (right_feeds == TriState::True) {
            return rules_detail::invalid(
                std::format("Curve belt cannot accept right side feeder, but it is fed from {0}", right_side_cell));
        }
        return rules_detail::valid();
    }

    if (from_feeds == TriState::False && left_feeds == TriState::True && right_feeds == TriState::False) {
        return rules_detail::invalid(std::format(
            "Straight belt has only left side feeder {0} and no flow from from_cell {1} or right side feeder {2}",
            left_side_cell, from, right_side_cell));
    }
    if (from_feeds == TriState::False && left_feeds == TriState::False && right_feeds == TriState::True) {
        return rules_detail::invalid(std::format(
            "Straight belt has only right side feeder {0} and no flow from from_cell {1} or left side feeder {2}",
            right_side_cell, from, left_side_cell));
    }
    return rules_detail::valid();
}

}  // namespace

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const BeltTile& belt) {
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }

    const Cell cell = make_cell(x, y);
    if (!tile_is_valid(Tile{belt}, cell)) {
        return rules_detail::invalid("Invalid belt from/to directions");
    }

    const Cell from = belt_from_cell(cell, belt);
    const Cell to = belt_to_cell(cell, belt);
    ValidationResult result = check_belt_topology(grid, cell, from, to, belt);
    if (!result.is_valid) {
        return result;
    }
    result = check_belt_resources(grid, cell, from, to, belt);
    if (!result.is_valid) {
        return result;
    }
    return rules_detail::valid();
}

}  // namespace fwfc
