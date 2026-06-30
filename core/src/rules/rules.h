#pragma once

#include "grid.h"
#include "tile.h"

#include <cstddef>
#include <string>

namespace fwfc {

struct ValidationResult {
    bool is_valid = true;
    std::string message;
};

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y);
ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const Tile& tile);
ValidationResult validate_grid(const Grid& grid);

}  // namespace fwfc
