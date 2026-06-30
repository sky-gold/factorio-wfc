#include "rules/input_belt_rules.h"

#include "cell.h"
#include "grid.h"
#include "rules/belt_flow.h"
#include "rules/rule_result.h"
#include "tile.h"

#include <format>
#include <optional>

namespace fwfc {
namespace {

bool target_belt_accepts_from_cell(Cell target_cell, const BeltTile& target_belt, Cell input_cell) {
    const Cell from = belt_from_cell(target_cell, target_belt);
    const Cell to = belt_to_cell(target_cell, target_belt);
    if (cell_equals(input_cell, from)) {
        return true;
    }
    if (cells_are_curve_neighbors(target_cell, from, to)) {
        return false;
    }

    const auto [left_side_cell, right_side_cell] = belt_side_cells(target_cell, target_belt);
    return cell_equals(input_cell, left_side_cell) || cell_equals(input_cell, right_side_cell);
}

bool target_accepts_input_from_cell(Cell target_cell, const Tile& target_tile, Cell input_cell) {
    return std::visit(
        overloaded{
            [](const EmptyTile&) { return false; },
            [&](const BeltTile& belt) { return target_belt_accepts_from_cell(target_cell, belt, input_cell); },
            [](const InputBeltTile&) { return false; },
            [&](const OutputBeltTile& output_belt) {
                return cell_equals(output_belt_from_cell(target_cell, output_belt), input_cell);
            },
        },
        target_tile);
}

}  // namespace

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const InputBeltTile& input_belt) {
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }

    const Cell cell = make_cell(x, y);
    if (!tile_is_valid(Tile{input_belt}, cell)) {
        return rules_detail::invalid("Invalid input belt direction");
    }

    const rules_detail::BeltLaneItems lanes{input_belt.left_item_id, input_belt.right_item_id};
    if (!rules_detail::has_lane_item(lanes)) {
        return rules_detail::valid();
    }

    const Cell target_cell = input_belt_to_cell(cell, input_belt);
    if (!grid.in_bounds(target_cell)) {
        return rules_detail::invalid(std::format("InputBelt at {0} requires output target {1}", cell, target_cell));
    }

    const std::optional<Tile> target_tile =
        grid.get(static_cast<std::size_t>(target_cell.x), static_cast<std::size_t>(target_cell.y));
    if (!target_tile.has_value()) {
        return rules_detail::valid();
    }
    if (!target_accepts_input_from_cell(target_cell, target_tile.value(), cell)) {
        return rules_detail::invalid(std::format("InputBelt at {0} cannot feed target tile at {1}", cell, target_cell));
    }

    return rules_detail::valid();
}

}  // namespace fwfc
