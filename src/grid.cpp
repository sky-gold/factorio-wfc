#include "grid.h"

#include <stdexcept>

namespace fwfc {

Grid::Grid(std::size_t width, std::size_t height)
    : width_(width), height_(height), cells_(width * height, std::nullopt) {}

bool Grid::in_bounds(std::size_t x, std::size_t y) const {
    return x < width_ && y < height_;
}

std::optional<Tile> Grid::get(std::size_t x, std::size_t y) const {
    if (!in_bounds(x, y)) {
        throw std::out_of_range("Grid::get out of bounds");
    }
    return cells_.at(index(x, y));
}

void Grid::set(std::size_t x, std::size_t y, std::optional<Tile> tile) {
    if (!in_bounds(x, y)) {
        throw std::out_of_range("Grid::set out of bounds");
    }
    cells_.at(index(x, y)) = std::move(tile);
}

std::size_t Grid::index(std::size_t x, std::size_t y) const {
    return y * width_ + x;
}

}  // namespace fwfc
