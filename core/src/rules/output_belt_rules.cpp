#include "rules/output_belt_rules.h"

#include "cell.h"
#include "grid.h"
#include "rules/belt_flow.h"
#include "rules/rule_result.h"
#include "tile.h"

#include <format>
#include <optional>

namespace fwfc {
namespace {

ValidationResult check_lane_matches(Cell cell, Cell feeder_cell, const char* lane_name, ItemId expected_item,
                                    ItemId incoming_item) {
    if (expected_item == incoming_item) {
        return rules_detail::valid();
    }
    return rules_detail::invalid(std::format(
        "OutputBelt at {0} expected item {1} on {2} lane from {3}, but incoming item is {4}", cell, expected_item,
        lane_name, feeder_cell, incoming_item));
}

}  // namespace

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y,
                                      const OutputBeltTile& output_belt) {
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }

    const Cell cell = make_cell(x, y);
    if (!tile_is_valid(Tile{output_belt}, cell)) {
        return rules_detail::invalid("Invalid output belt direction");
    }

    const rules_detail::BeltLaneItems expected_lanes{output_belt.left_item_id, output_belt.right_item_id};
    if (!rules_detail::has_lane_item(expected_lanes)) {
        return rules_detail::valid();
    }

    const Cell feeder_cell = output_belt_from_cell(cell, output_belt);
    if (!grid.in_bounds(feeder_cell)) {
        return rules_detail::invalid(std::format("OutputBelt at {0} requires input from {1}", cell, feeder_cell));
    }

    const std::optional<Tile> feeder_tile =
        grid.get(static_cast<std::size_t>(feeder_cell.x), static_cast<std::size_t>(feeder_cell.y));
    if (!feeder_tile.has_value()) {
        return rules_detail::valid();
    }

    const std::optional<rules_detail::BeltLaneItems> incoming_lanes =
        rules_detail::outgoing_lane_items_to_cell(feeder_cell, cell, feeder_tile.value());
    if (!incoming_lanes.has_value()) {
        return rules_detail::invalid(std::format("OutputBelt at {0} is not fed from {1}", cell, feeder_cell));
    }

    ValidationResult result =
        check_lane_matches(cell, feeder_cell, "left", expected_lanes.left_item_id, incoming_lanes.value().left_item_id);
    if (!result.is_valid) {
        return result;
    }
    result = check_lane_matches(cell, feeder_cell, "right", expected_lanes.right_item_id,
                                incoming_lanes.value().right_item_id);
    if (!result.is_valid) {
        return result;
    }

    return rules_detail::valid();
}

}  // namespace fwfc
