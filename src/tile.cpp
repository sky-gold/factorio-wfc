#include "tile.h"

namespace fwfc {

TileType get_tile_type(const Tile& tile) {
    return std::visit([](const EmptyTile&) { return TileType::Empty; }, tile);
}

}  // namespace fwfc
