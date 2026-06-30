#include "cell.h"

namespace fwfc {

bool cell_equals(Cell a, Cell b) { return a.x == b.x && a.y == b.y; }

bool cell_is_neighbor(Cell center, Cell other) {
    const int dx = other.x - center.x;
    const int dy = other.y - center.y;
    return (dx == 0 && (dy == 1 || dy == -1)) || (dy == 0 && (dx == 1 || dx == -1));
}

bool cells_are_opposite_neighbors(Cell center, Cell a, Cell b) {
    if (!cell_is_neighbor(center, a) || !cell_is_neighbor(center, b)) {
        return false;
    }
    return a.x + b.x == 2 * center.x && a.y + b.y == 2 * center.y;
}

bool cells_are_curve_neighbors(Cell center, Cell from, Cell to) {
    if (!cell_is_neighbor(center, from) || !cell_is_neighbor(center, to)) {
        return false;
    }
    return !cells_are_opposite_neighbors(center, from, to);
}

Cell cell_offset(Cell c, int dx, int dy) { return {c.x + dx, c.y + dy}; }

Cell make_cell(std::size_t x, std::size_t y) {
    return {static_cast<int>(x), static_cast<int>(y)};
}

Cell cell_in_direction(Cell center, Direction d) {
    switch (d) {
        case Direction::North:
            return cell_offset(center, -1, 0);
        case Direction::East:
            return cell_offset(center, 0, 1);
        case Direction::South:
            return cell_offset(center, 1, 0);
        case Direction::West:
            return cell_offset(center, 0, -1);
    }
    return center;
}

std::vector<Cell> cardinal_neighbors(Cell center) {
    return {
        cell_offset(center, -1, 0),
        cell_offset(center, 0, 1),
        cell_offset(center, 1, 0),
        cell_offset(center, 0, -1),
    };
}

std::pair<Cell, Cell> side_cells(Cell center, Cell from, Cell to) {
    std::vector<Cell> sides;
    for (const Cell neighbor : cardinal_neighbors(center)) {
        if (!cell_equals(neighbor, from) && !cell_equals(neighbor, to)) {
            sides.push_back(neighbor);
        }
    }
    if (sides.size() > 2) {
        throw std::runtime_error("cell must have exactly 2 side cells");
    }
    return {sides[0], sides[1]};
}

}  // namespace fwfc
