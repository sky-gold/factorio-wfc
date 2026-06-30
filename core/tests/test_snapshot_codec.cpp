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

void write_input_belt_cell(std::vector<std::uint8_t>& cells,
                           std::size_t cell_index,
                           std::uint8_t to_dir,
                           std::uint32_t left_item_id,
                           std::uint32_t right_item_id,
                           double left_max_rate,
                           double right_max_rate) {
    const std::size_t offset = cell_index * kCellStride;
    cells[offset] = kTypeIdInputBelt;
    cells[offset + 1] = to_dir;
    std::memcpy(cells.data() + offset + 4, &left_item_id, sizeof(left_item_id));
    std::memcpy(cells.data() + offset + 8, &right_item_id, sizeof(right_item_id));
    std::memcpy(cells.data() + offset + 12, &left_max_rate, sizeof(left_max_rate));
    std::memcpy(cells.data() + offset + 20, &right_max_rate, sizeof(right_max_rate));
}

void write_output_belt_cell(std::vector<std::uint8_t>& cells,
                            std::size_t cell_index,
                            std::uint8_t from_dir,
                            std::uint32_t left_item_id,
                            std::uint32_t right_item_id,
                            double left_min_rate,
                            double right_min_rate) {
    const std::size_t offset = cell_index * kCellStride;
    cells[offset] = kTypeIdOutputBelt;
    cells[offset + 1] = from_dir;
    std::memcpy(cells.data() + offset + 4, &left_item_id, sizeof(left_item_id));
    std::memcpy(cells.data() + offset + 8, &right_item_id, sizeof(right_item_id));
    std::memcpy(cells.data() + offset + 12, &left_min_rate, sizeof(left_min_rate));
    std::memcpy(cells.data() + offset + 20, &right_min_rate, sizeof(right_min_rate));
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
    EXPECT_FALSE(grid.get(0, 1).has_value());
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

    const auto tile = grid.get(0, 1);
    ASSERT_TRUE(tile.has_value());
    EXPECT_EQ(get_tile_type(*tile), TileType::Belt);

    const auto* belt = std::get_if<BeltTile>(&(*tile));
    ASSERT_NE(belt, nullptr);
    EXPECT_EQ(belt->from_dir, Direction::West);
    EXPECT_EQ(belt->to_dir, Direction::East);
    EXPECT_EQ(belt->left_item_id, kEmptyItemId);
    EXPECT_EQ(belt->right_item_id, kEmptyItemId);

    EXPECT_TRUE(cell_equals(belt_from_cell(Cell{0, 1}, *belt), Cell{0, 0}));
    EXPECT_TRUE(cell_equals(belt_to_cell(Cell{0, 1}, *belt), Cell{0, 2}));
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
    EXPECT_EQ(belt->from_dir, Direction::South);
    EXPECT_EQ(belt->to_dir, Direction::East);
    EXPECT_EQ(belt->left_item_id, 1u);
    EXPECT_EQ(belt->right_item_id, 2u);

    const Cell center{0, 0};
    const Cell from = belt_from_cell(center, *belt);
    const Cell to = belt_to_cell(center, *belt);
    EXPECT_TRUE(cell_equals(from, Cell{1, 0}));
    EXPECT_TRUE(cell_equals(to, Cell{0, 1}));
    EXPECT_TRUE(cells_are_curve_neighbors(center, from, to));
}

TEST(SnapshotCodecTest, RejectsInvalidBeltDirection) {
    std::vector<std::uint8_t> cells(1 * 1 * kCellStride, kCellTagUndecided);
    write_belt_cell(cells, 0, 4, static_cast<std::uint8_t>(Direction::East), kEmptyItemId, kEmptyItemId);

    Grid grid(1, 1);
    std::string error;
    EXPECT_FALSE(decode_snapshot(1, 1, {cells.data(), cells.size()}, grid, error));
    EXPECT_FALSE(error.empty());
}

TEST(SnapshotCodecTest, DecodeInputBeltWithRates) {
    std::vector<std::uint8_t> cells(1 * 1 * kCellStride, kCellTagUndecided);
    write_input_belt_cell(cells, 0, static_cast<std::uint8_t>(Direction::East), 1, 2, 3.5, 4.25);

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(1, 1, {cells.data(), cells.size()}, grid, error)) << error;

    const auto tile = grid.get(0, 0);
    ASSERT_TRUE(tile.has_value());
    EXPECT_EQ(get_tile_type(tile.value()), TileType::InputBelt);

    const auto* input_belt = std::get_if<InputBeltTile>(&tile.value());
    ASSERT_NE(input_belt, nullptr);
    EXPECT_EQ(input_belt->to_dir, Direction::East);
    EXPECT_EQ(input_belt->left_item_id, 1u);
    EXPECT_EQ(input_belt->right_item_id, 2u);
    EXPECT_DOUBLE_EQ(input_belt->left_max_rate, 3.5);
    EXPECT_DOUBLE_EQ(input_belt->right_max_rate, 4.25);
}

TEST(SnapshotCodecTest, DecodeOutputBeltWithRates) {
    std::vector<std::uint8_t> cells(1 * 1 * kCellStride, kCellTagUndecided);
    write_output_belt_cell(cells, 0, static_cast<std::uint8_t>(Direction::West), 1, 2, 1.5, 2.75);

    Grid grid(1, 1);
    std::string error;
    ASSERT_TRUE(decode_snapshot(1, 1, {cells.data(), cells.size()}, grid, error)) << error;

    const auto tile = grid.get(0, 0);
    ASSERT_TRUE(tile.has_value());
    EXPECT_EQ(get_tile_type(tile.value()), TileType::OutputBelt);

    const auto* output_belt = std::get_if<OutputBeltTile>(&tile.value());
    ASSERT_NE(output_belt, nullptr);
    EXPECT_EQ(output_belt->from_dir, Direction::West);
    EXPECT_EQ(output_belt->left_item_id, 1u);
    EXPECT_EQ(output_belt->right_item_id, 2u);
    EXPECT_DOUBLE_EQ(output_belt->left_min_rate, 1.5);
    EXPECT_DOUBLE_EQ(output_belt->right_min_rate, 2.75);
}

TEST(SnapshotCodecTest, RejectsInvalidInputOutputBeltDirection) {
    std::vector<std::uint8_t> cells(2 * 1 * kCellStride, kCellTagUndecided);
    write_input_belt_cell(cells, 0, 4, 1, 2, 3.5, 4.25);
    write_output_belt_cell(cells, 1, static_cast<std::uint8_t>(Direction::West), 1, 2, 1.5, 2.75);

    Grid grid(1, 1);
    std::string error;
    EXPECT_FALSE(decode_snapshot(2, 1, {cells.data(), cells.size()}, grid, error));
    EXPECT_NE(error.find("input belt"), std::string::npos);

    write_input_belt_cell(cells, 0, static_cast<std::uint8_t>(Direction::East), 1, 2, 3.5, 4.25);
    write_output_belt_cell(cells, 1, 5, 1, 2, 1.5, 2.75);
    EXPECT_FALSE(decode_snapshot(2, 1, {cells.data(), cells.size()}, grid, error));
    EXPECT_NE(error.find("output belt"), std::string::npos);
}

}  // namespace
}  // namespace fwfc::wire
