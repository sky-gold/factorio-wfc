#include <gtest/gtest.h>

#include "grid.h"
#include "rules/rules.h"
#include "tile.h"
#include "types.h"

namespace fwfc {
namespace {

constexpr ItemId kIron = 1;
constexpr ItemId kCopper = 2;

Grid empty_grid(std::size_t width, std::size_t height) {
    Grid grid(width, height);
    for (std::size_t x = 0; x < height; ++x) {
        for (std::size_t y = 0; y < width; ++y) {
            grid.set(x, y, EmptyTile{});
        }
    }
    return grid;
}

void belt(Grid& grid,
          std::size_t x,
          std::size_t y,
          Direction from_dir,
          Direction to_dir,
          ItemId left_item = kEmptyItemId,
          ItemId right_item = kEmptyItemId) {
    BeltTile tile;
    tile.from_dir = from_dir;
    tile.to_dir = to_dir;
    tile.left_item_id = left_item;
    tile.right_item_id = right_item;
    grid.set(x, y, tile);
}

void input_belt(Grid& grid,
                std::size_t x,
                std::size_t y,
                Direction to_dir,
                ItemId left_item = kEmptyItemId,
                ItemId right_item = kEmptyItemId,
                double left_max_rate = 0.0,
                double right_max_rate = 0.0) {
    InputBeltTile tile;
    tile.to_dir = to_dir;
    tile.left_item_id = left_item;
    tile.right_item_id = right_item;
    tile.left_max_rate = left_max_rate;
    tile.right_max_rate = right_max_rate;
    grid.set(x, y, tile);
}

void output_belt(Grid& grid,
                 std::size_t x,
                 std::size_t y,
                 Direction from_dir,
                 ItemId left_item = kEmptyItemId,
                 ItemId right_item = kEmptyItemId,
                 double left_min_rate = 0.0,
                 double right_min_rate = 0.0) {
    OutputBeltTile tile;
    tile.from_dir = from_dir;
    tile.left_item_id = left_item;
    tile.right_item_id = right_item;
    tile.left_min_rate = left_min_rate;
    tile.right_min_rate = right_min_rate;
    grid.set(x, y, tile);
}

TEST(InputOutputBelts, InputBeltFeedsBeltWithMatchingLane) {
    Grid grid = empty_grid(2, 1);
    input_belt(grid, 0, 0, Direction::East, kEmptyItemId, kIron, 0.0, 3.5);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kIron);

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

TEST(InputOutputBelts, BeltFeedsOutputBeltWithMatchingLane) {
    Grid grid = empty_grid(3, 1);
    input_belt(grid, 0, 0, Direction::East, kEmptyItemId, kIron, 0.0, 3.5);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kIron);
    output_belt(grid, 0, 2, Direction::West, kEmptyItemId, kIron, 0.0, 2.0);

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

TEST(InputOutputBelts, OutputBeltLaneMismatchInvalid) {
    Grid grid = empty_grid(3, 1);
    input_belt(grid, 0, 0, Direction::East, kEmptyItemId, kCopper, 0.0, 3.5);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kCopper);
    output_belt(grid, 0, 2, Direction::West, kEmptyItemId, kIron, 0.0, 2.0);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("expected item"), std::string::npos) << result.message;
}

TEST(InputOutputBelts, UndecidedNeighborAllowed) {
    Grid input_grid(2, 1);
    input_belt(input_grid, 0, 0, Direction::East, kEmptyItemId, kIron, 0.0, 3.5);
    EXPECT_TRUE(validate_placed_tile(input_grid, 0, 0).is_valid);

    Grid output_grid(2, 1);
    output_belt(output_grid, 0, 1, Direction::West, kEmptyItemId, kIron, 0.0, 2.0);
    EXPECT_TRUE(validate_placed_tile(output_grid, 0, 1).is_valid);
}

TEST(InputOutputBelts, InputBeltWithExplicitEmptyTargetInvalid) {
    Grid grid = empty_grid(2, 1);
    input_belt(grid, 0, 0, Direction::East, kEmptyItemId, kIron, 0.0, 3.5);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("cannot feed target tile"), std::string::npos) << result.message;
}

TEST(InputOutputBelts, OutputBeltWithExplicitEmptyFeederInvalid) {
    Grid grid = empty_grid(2, 1);
    output_belt(grid, 0, 1, Direction::West, kEmptyItemId, kIron, 0.0, 2.0);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("is not fed"), std::string::npos) << result.message;
}

TEST(InputOutputBelts, InputBeltCanFeedOutputBeltDirectly) {
    Grid grid = empty_grid(2, 1);
    input_belt(grid, 0, 0, Direction::East, kIron, kEmptyItemId, 1.0, 0.0);
    output_belt(grid, 0, 1, Direction::West, kIron, kEmptyItemId, 1.0, 0.0);

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

}  // namespace
}  // namespace fwfc
