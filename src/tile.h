#pragma once

#include "cell.h"
#include "types.h"

#include <cstdint>
#include <variant>

namespace fwfc {

enum class TileType : std::uint8_t {
    Empty = 0,
    Belt = 10,
};

struct EmptyTile {
    static constexpr TileType type = TileType::Empty;
};

struct BeltTile {
    static constexpr TileType type = TileType::Belt;
    Cell from_cell{};
    Cell to_cell{};
    ItemId left_item_id = kEmptyItemId;
    ItemId right_item_id = kEmptyItemId;
};

using Tile = std::variant<EmptyTile, BeltTile>;

TileType get_tile_type(const Tile& tile);

}  // namespace fwfc
