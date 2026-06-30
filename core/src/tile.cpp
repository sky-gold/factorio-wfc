#include "tile.h"

#include "cell.h"

#include <type_traits>

namespace fwfc {
namespace {

bool directions_are_opposite(Direction a, Direction b) {
    return (a == Direction::North && b == Direction::South) ||
           (a == Direction::South && b == Direction::North) ||
           (a == Direction::East && b == Direction::West) ||
           (a == Direction::West && b == Direction::East);
}

bool direction_is_valid(Direction direction) {
    return direction == Direction::North || direction == Direction::East || direction == Direction::South ||
           direction == Direction::West;
}

std::pair<Cell, Cell> straight_belt_side_cells(Cell center, Direction flow) {
    switch (flow) {
        case Direction::North:
            return {cell_in_direction(center, Direction::West), cell_in_direction(center, Direction::East)};
        case Direction::East:
            return {cell_in_direction(center, Direction::North), cell_in_direction(center, Direction::South)};
        case Direction::South:
            return {cell_in_direction(center, Direction::East), cell_in_direction(center, Direction::West)};
        case Direction::West:
            return {cell_in_direction(center, Direction::South), cell_in_direction(center, Direction::North)};
    }
    return {center, center};
}

}  // namespace

TileType get_tile_type(const Tile& tile) {
    return std::visit([](const auto& t) { return t.type; }, tile);
}

bool belt_dirs_valid(Direction from_dir, Direction to_dir) { return from_dir != to_dir; }

Cell belt_from_cell(Cell center, const BeltTile& belt) {
    return cell_in_direction(center, belt.from_dir);
}

Cell belt_to_cell(Cell center, const BeltTile& belt) {
    return cell_in_direction(center, belt.to_dir);
}

std::pair<Cell, Cell> belt_side_cells(Cell center, const BeltTile& belt) {
    if (directions_are_opposite(belt.from_dir, belt.to_dir)) {
        return straight_belt_side_cells(center, belt.to_dir);
    }
    return side_cells(center, belt_from_cell(center, belt), belt_to_cell(center, belt));
}

Cell input_belt_to_cell(Cell center, const InputBeltTile& input_belt) {
    return cell_in_direction(center, input_belt.to_dir);
}

Cell output_belt_from_cell(Cell center, const OutputBeltTile& output_belt) {
    return cell_in_direction(center, output_belt.from_dir);
}

bool tile_is_valid(const Tile& tile, Cell cell) {
    (void)cell;
    return std::visit(
        [&](const auto& t) -> bool {
            using T = std::decay_t<decltype(t)>;
            if constexpr (std::is_same_v<T, EmptyTile>) {
                return true;
            } else if constexpr (std::is_same_v<T, BeltTile>) {
                return direction_is_valid(t.from_dir) && direction_is_valid(t.to_dir) &&
                       belt_dirs_valid(t.from_dir, t.to_dir);
            } else if constexpr (std::is_same_v<T, InputBeltTile>) {
                return direction_is_valid(t.to_dir);
            } else if constexpr (std::is_same_v<T, OutputBeltTile>) {
                return direction_is_valid(t.from_dir);
            } else {
                return false;
            }
        },
        tile);
}

}  // namespace fwfc
