#pragma once

#include "tile.h"

#include <cstddef>
#include <optional>
#include <vector>

namespace fwfc {

class Grid {
public:
    Grid(std::size_t width, std::size_t height);

    std::size_t width() const { return width_; }
    std::size_t height() const { return height_; }

    bool in_bounds(std::size_t x, std::size_t y) const;
    std::optional<Tile> get(std::size_t x, std::size_t y) const;
    void set(std::size_t x, std::size_t y, std::optional<Tile> tile);

private:
    std::size_t width_;
    std::size_t height_;
    std::vector<std::optional<Tile>> cells_;

    std::size_t index(std::size_t x, std::size_t y) const;
};

}  // namespace fwfc
