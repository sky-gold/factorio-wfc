#pragma once

#include "cell.h"
#include "overloaded.h"
#include "tile.h"
#include "types.h"

#include <optional>
#include <variant>

namespace fwfc::rules_detail {

struct BeltLaneItems {
    ItemId left_item_id = kEmptyItemId;
    ItemId right_item_id = kEmptyItemId;
};

inline bool has_lane_item(BeltLaneItems lanes) {
    return lanes.left_item_id != kEmptyItemId || lanes.right_item_id != kEmptyItemId;
}

inline std::optional<BeltLaneItems> outgoing_lane_items_to_cell(Cell tile_cell, Cell target_cell, const Tile& tile) {
    return std::visit(
        overloaded{
            [](const EmptyTile&) -> std::optional<BeltLaneItems> { return std::nullopt; },
            [&](const BeltTile& belt) -> std::optional<BeltLaneItems> {
                if (cell_equals(belt_to_cell(tile_cell, belt), target_cell)) {
                    return BeltLaneItems{belt.left_item_id, belt.right_item_id};
                }
                return std::nullopt;
            },
            [&](const InputBeltTile& input_belt) -> std::optional<BeltLaneItems> {
                if (cell_equals(input_belt_to_cell(tile_cell, input_belt), target_cell)) {
                    return BeltLaneItems{input_belt.left_item_id, input_belt.right_item_id};
                }
                return std::nullopt;
            },
            [](const OutputBeltTile&) -> std::optional<BeltLaneItems> { return std::nullopt; },
        },
        tile);
}

}  // namespace fwfc::rules_detail
