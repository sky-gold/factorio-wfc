#pragma once

#include "grid.h"
#include "rules/rules.h"
#include "tile.h"

#include <cstddef>

namespace fwfc {

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const BeltTile& tile);

}  // namespace fwfc
