#include <gtest/gtest.h>

#include "catalog.h"
#include "validate.h"
#include "wire/wire_format.h"

#include <vector>

namespace fwfc {
namespace {

TEST(ValidationSnapshotTest, RequiresCatalog) {
    reset_session_for_test();
    std::vector<std::uint8_t> cells(4 * wire::kCellStride, wire::kCellTagUndecided);
    const ValidationResult result = validate_snapshot(2, 2, {cells.data(), cells.size()});
    EXPECT_FALSE(result.is_valid);
    EXPECT_FALSE(result.message.empty());
}

TEST(ValidationSnapshotTest, ValidUndecidedGrid) {
    set_session_catalog(Catalog{});
    std::vector<std::uint8_t> cells(4 * wire::kCellStride, wire::kCellTagUndecided);
    const ValidationResult result = validate_snapshot(2, 2, {cells.data(), cells.size()});
    EXPECT_TRUE(result.is_valid);
    EXPECT_TRUE(result.message.empty());
}

TEST(ValidationSnapshotTest, ValidMixedGrid) {
    set_session_catalog(Catalog{});
    std::vector<std::uint8_t> cells(9 * wire::kCellStride, wire::kCellTagUndecided);
    cells[0] = wire::kCellTagEmpty;
    cells[2 * wire::kCellStride] = wire::kCellTagEmpty;
    const ValidationResult result = validate_snapshot(3, 3, {cells.data(), cells.size()});
    EXPECT_TRUE(result.is_valid);
}

}  // namespace
}  // namespace fwfc
