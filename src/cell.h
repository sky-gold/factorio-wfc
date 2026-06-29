#pragma once

#include "types.h"

#include <cstddef>
#include <utility>
#include <vector>

namespace fwfc {

struct Cell {
    int x = 0;
    int y = 0;
};

bool cell_equals(Cell a, Cell b);
bool cell_in_grid(Cell c, std::size_t grid_width, std::size_t grid_height);
bool cell_is_neighbor(Cell center, Cell other);
bool cells_are_opposite_neighbors(Cell center, Cell a, Cell b);
bool cells_are_curve_neighbors(Cell center, Cell from, Cell to);

Cell cell_offset(Cell c, int dx, int dy);
Cell cell_in_direction(Cell center, Direction d);
std::vector<Cell> cardinal_neighbors(Cell center);
std::pair<Cell, Cell> side_cells(Cell center, Cell from, Cell to);

}  // namespace fwfc
