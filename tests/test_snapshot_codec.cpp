#include <gtest/gtest.h>

#include "grid.h"
#include "wire/snapshot_codec.h"
#include "wire/wire_format.h"

#include <vector>

namespace fwfc::wire {
namespace {

TEST(SnapshotCodecTest, DecodeUndecidedGrid) {
    std::vector<std::uint8_t> cells(2 * 2 * kCellStride, kCellTagUndecided);

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(2, 2, {cells.data(), cells.size()}, grid, error)) << error;
    EXPECT_FALSE(grid.get(0, 0).has_value());
    EXPECT_FALSE(grid.get(1, 1).has_value());
}

TEST(SnapshotCodecTest, DecodeMixedGrid) {
    std::vector<std::uint8_t> cells(2 * 1 * kCellStride, kCellTagUndecided);
    cells[0] = kCellTagEmpty;
    cells[kCellStride] = kCellTagUndecided;

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(2, 1, {cells.data(), cells.size()}, grid, error)) << error;
    ASSERT_TRUE(grid.get(0, 0).has_value());
    EXPECT_EQ(get_tile_type(*grid.get(0, 0)), TileType::Empty);
    EXPECT_FALSE(grid.get(1, 0).has_value());
}

TEST(SnapshotCodecTest, RejectsWrongBufferSize) {
    std::vector<std::uint8_t> cells(kCellStride, kCellTagUndecided);
    Grid grid(1, 1);
    std::string error;
    EXPECT_FALSE(decode_snapshot(2, 2, {cells.data(), cells.size()}, grid, error));
    EXPECT_FALSE(error.empty());
}

}  // namespace
}  // namespace fwfc::wire
