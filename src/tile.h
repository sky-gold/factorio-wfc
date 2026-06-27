#pragma once

#include <cstdint>
#include <variant>

namespace fwfc {

enum class TileType : std::uint8_t {
    Empty = 0,
};

struct EmptyTile {
    static constexpr TileType type = TileType::Empty;
};

using Tile = std::variant<EmptyTile>;

TileType get_tile_type(const Tile& tile);

}  // namespace fwfc
