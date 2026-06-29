#include <gtest/gtest.h>

#include "cell.h"
#include "grid.h"
#include "tile.h"
#include "types.h"
#include "wire/snapshot_codec.h"
#include "wire/wire_format.h"

#include <cstring>
#include <vector>

namespace fwfc::wire {
namespace {

void write_belt_cell(std::vector<std::uint8_t>& cells,
                     std::size_t cell_index,
                     std::uint8_t from_dir,
                     std::uint8_t to_dir,
                     std::uint32_t left_item_id,
                     std::uint32_t right_item_id) {
    const std::size_t offset = cell_index * kCellStride;
    cells[offset] = kTypeIdBelt;
    cells[offset + 1] = from_dir;
    cells[offset + 2] = to_dir;
    cells[offset + 3] = 0;
    std::memcpy(cells.data() + offset + 4, &left_item_id, sizeof(left_item_id));
    std::memcpy(cells.data() + offset + 8, &right_item_id, sizeof(right_item_id));
}

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

TEST(SnapshotCodecTest, DecodeStraightBeltWestToEast) {
    std::vector<std::uint8_t> cells(3 * 1 * kCellStride, kCellTagUndecided);
    write_belt_cell(cells, 1, static_cast<std::uint8_t>(Direction::West),
                    static_cast<std::uint8_t>(Direction::East), kEmptyItemId, kEmptyItemId);

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(3, 1, {cells.data(), cells.size()}, grid, error)) << error;

    const auto tile = grid.get(1, 0);
    ASSERT_TRUE(tile.has_value());
    EXPECT_EQ(get_tile_type(*tile), TileType::Belt);

    const auto* belt = std::get_if<BeltTile>(&(*tile));
    ASSERT_NE(belt, nullptr);
    EXPECT_TRUE(cell_equals(belt->from_cell, Cell{0, 0}));
    EXPECT_TRUE(cell_equals(belt->to_cell, Cell{2, 0}));
    EXPECT_EQ(belt->left_item_id, kEmptyItemId);
    EXPECT_EQ(belt->right_item_id, kEmptyItemId);
}

TEST(SnapshotCodecTest, DecodeCornerBeltSouthToEast) {
    std::vector<std::uint8_t> cells(1 * 1 * kCellStride, kCellTagUndecided);
    write_belt_cell(cells, 0, static_cast<std::uint8_t>(Direction::South),
                    static_cast<std::uint8_t>(Direction::East), 1, 2);

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(1, 1, {cells.data(), cells.size()}, grid, error)) << error;

    const auto tile = grid.get(0, 0);
    ASSERT_TRUE(tile.has_value());
    EXPECT_EQ(get_tile_type(*tile), TileType::Belt);

    const auto* belt = std::get_if<BeltTile>(&(*tile));
    ASSERT_NE(belt, nullptr);
    EXPECT_TRUE(cell_equals(belt->from_cell, Cell{0, 1}));
    EXPECT_TRUE(cell_equals(belt->to_cell, Cell{1, 0}));
    EXPECT_EQ(belt->left_item_id, 1u);
    EXPECT_EQ(belt->right_item_id, 2u);
    EXPECT_TRUE(cells_are_curve_neighbors(Cell{0, 0}, belt->from_cell, belt->to_cell));
}

TEST(SnapshotCodecTest, RejectsInvalidBeltDirection) {
    std::vector<std::uint8_t> cells(1 * 1 * kCellStride, kCellTagUndecided);
    write_belt_cell(cells, 0, 4, static_cast<std::uint8_t>(Direction::East), kEmptyItemId, kEmptyItemId);

    Grid grid(1, 1);
    std::string error;
    EXPECT_FALSE(decode_snapshot(1, 1, {cells.data(), cells.size()}, grid, error));
    EXPECT_FALSE(error.empty());
}

}  // namespace
}  // namespace fwfc::wire
