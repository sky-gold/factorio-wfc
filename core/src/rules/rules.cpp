#include "rules/rules.h"

#include "rules/belt_rules.h"
#include "rules/empty_rules.h"
#include "rules/input_belt_rules.h"
#include "rules/output_belt_rules.h"
#include "rules/rule_result.h"

#include <optional>
#include <string>
#include <variant>

namespace fwfc {

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y) {
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }

    const std::optional<Tile> tile = grid.get(x, y);
    if (!tile.has_value()) {
        return rules_detail::valid();
    }
    return validate_placed_tile(grid, x, y, tile.value());
}

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const Tile& tile) {
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }

    return std::visit(
        [&](const auto& typed_tile) {
            return validate_placed_tile(grid, x, y, typed_tile);
        },
        tile);
}

ValidationResult validate_grid(const Grid& grid) {
    for (std::size_t x = 0; x < grid.height(); ++x) {
        for (std::size_t y = 0; y < grid.width(); ++y) {
            ValidationResult tile_result = validate_placed_tile(grid, x, y);
            if (!tile_result.is_valid) {
                return rules_detail::invalid("at (" + std::to_string(x) + "," + std::to_string(y) + "): " +
                                             tile_result.message);
            }
        }
    }
    return rules_detail::valid();
}

}  // namespace fwfc
