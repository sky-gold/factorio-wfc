#include "rules/empty_rules.h"

#include "rules/rule_result.h"

namespace fwfc {

ValidationResult validate_placed_tile(const Grid& grid, std::size_t x, std::size_t y, const EmptyTile& tile) {
    (void)tile;
    if (!grid.in_bounds(x, y)) {
        return rules_detail::invalid("Out of bounds");
    }
    return rules_detail::valid();
}

}  // namespace fwfc
