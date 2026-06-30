#pragma once

#include "cell.h"
#include "types.h"

#include <cstdint>
#include <variant>

namespace fwfc {

enum class TileType : std::uint8_t {
    Empty = 0,
    Belt = 10,
    InputBelt = 11,
    OutputBelt = 12,
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

struct InputBeltTile {
    static constexpr TileType type = TileType::InputBelt;
    Direction to_dir = Direction::North;
    ItemId left_item_id = kEmptyItemId;
    ItemId right_item_id = kEmptyItemId;
    double left_max_rate = 0.0;
    double right_max_rate = 0.0;
};

struct OutputBeltTile {
    static constexpr TileType type = TileType::OutputBelt;
    Direction from_dir = Direction::North;
    ItemId left_item_id = kEmptyItemId;
    ItemId right_item_id = kEmptyItemId;
    double left_min_rate = 0.0;
    double right_min_rate = 0.0;
};

using Tile = std::variant<EmptyTile, BeltTile, InputBeltTile, OutputBeltTile>;

TileType get_tile_type(const Tile& tile);

bool belt_dirs_valid(Direction from_dir, Direction to_dir);

Cell belt_from_cell(Cell center, const BeltTile& belt);
Cell belt_to_cell(Cell center, const BeltTile& belt);
std::pair<Cell, Cell> belt_side_cells(Cell center, const BeltTile& belt);
Cell input_belt_to_cell(Cell center, const InputBeltTile& input_belt);
Cell output_belt_from_cell(Cell center, const OutputBeltTile& output_belt);

bool tile_is_valid(const Tile& tile, Cell cell);

}  // namespace fwfc
