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
    Direction from_dir = Direction::North;
    Direction to_dir = Direction::North;
    ItemId left_item_id = kEmptyItemId;
    ItemId right_item_id = kEmptyItemId;
};

using Tile = std::variant<EmptyTile, BeltTile>;

TileType get_tile_type(const Tile& tile);

bool belt_dirs_valid(Direction from_dir, Direction to_dir);

Cell belt_from_cell(Cell center, const BeltTile& belt);
Cell belt_to_cell(Cell center, const BeltTile& belt);
std::pair<Cell, Cell> belt_side_cells(Cell center, const BeltTile& belt);

bool tile_is_valid(const Tile& tile, Cell cell);

}  // namespace fwfc
