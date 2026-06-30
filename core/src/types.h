#pragma once

#include <cstdint>
#include <limits>

namespace fwfc {

using ItemId = std::uint32_t;
using RecipeId = std::uint32_t;

inline constexpr ItemId kEmptyItemId = std::numeric_limits<ItemId>::max();
inline constexpr RecipeId kInvalidRecipeId = std::numeric_limits<RecipeId>::max();

enum class Direction : std::uint8_t { North = 0, East = 1, South = 2, West = 3 };

enum class TriState : std::uint8_t {
    False = 0,
    True = 1,
    Unknown = 2,
};

}  // namespace fwfc
