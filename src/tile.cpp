#include "tile.h"

namespace fwfc {

TileType get_tile_type(const Tile& tile) {
    return std::visit([](const auto& t) { return t.type; }, tile);
}

}  // namespace fwfc
