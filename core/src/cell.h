#pragma once

#include "types.h"

#include <cstddef>
#include <format>
#include <utility>
#include <vector>

namespace fwfc {

// Grid coordinates: x = row (0 at top, increases downward), y = column (0 at left).
struct Cell {
    int x = 0;
    int y = 0;
};

bool cell_equals(Cell a, Cell b);
bool cell_is_neighbor(Cell center, Cell other);
bool cells_are_opposite_neighbors(Cell center, Cell a, Cell b);
bool cells_are_curve_neighbors(Cell center, Cell from, Cell to);

Cell make_cell(std::size_t x, std::size_t y);
Cell cell_offset(Cell c, int dx, int dy);
Cell cell_in_direction(Cell center, Direction d);
std::vector<Cell> cardinal_neighbors(Cell center);
std::pair<Cell, Cell> side_cells(Cell center, Cell from, Cell to);

}  // namespace fwfc

template <>
struct std::formatter<fwfc::Cell> {
    constexpr auto parse(std::format_parse_context& ctx) { return ctx.begin(); }

    auto format(const fwfc::Cell& c, std::format_context& ctx) const {
        return std::format_to(ctx.out(), "({}, {})", c.x, c.y);
    }
};
