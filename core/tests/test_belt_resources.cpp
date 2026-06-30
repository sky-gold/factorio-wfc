#include <gtest/gtest.h>

#include "grid.h"
#include "tile.h"
#include "types.h"
#include "rules/rules.h"

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

void belt(Grid& grid, std::size_t x, std::size_t y, Direction from_dir, Direction to_dir,
          ItemId left_item = kEmptyItemId, ItemId right_item = kEmptyItemId) {
    BeltTile b;
    b.from_dir = from_dir;
    b.to_dir = to_dir;
    b.left_item_id = left_item;
    b.right_item_id = right_item;
    grid.set(x, y, b);
}

// ---------------------------------------------------------------------------
// Один belt между двумя Empty — item без источника и приёмника.
//   (0,0) empty — (0,1) belt W→E, right=iron — (0,2) empty
// ---------------------------------------------------------------------------
TEST(BeltResources, LaneItemBetweenEmptyTiles_Invalid) {
    Grid grid = empty_grid(3, 1);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kIron);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("no input on right side"), std::string::npos)
        << "got: " << result.message;
}

// ---------------------------------------------------------------------------
// Цепочка 3 belt W→E, iron на правой полосе.
//   (0,0) undecided (будущий input_belt) — (0,1) W→E — (0,2) W→E
// ---------------------------------------------------------------------------
TEST(BeltResources, ThreeBeltChain_MatchingLane_Valid) {
    Grid grid(3, 1);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kIron);
    belt(grid, 0, 2, Direction::West, Direction::East, kEmptyItemId, kIron);

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

// ---------------------------------------------------------------------------
// Цепочка с mismatch на среднем belt. (0,0) undecided.
// ---------------------------------------------------------------------------
TEST(BeltResources, ThreeBeltChain_LaneMismatch_Invalid) {
    Grid grid(3, 1);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kCopper);
    belt(grid, 0, 2, Direction::West, Direction::East, kEmptyItemId, kIron);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("expected item is"), std::string::npos) << result.message;
}

// ---------------------------------------------------------------------------
// Belt с item, from_cell undecided (WFC).
//   grid 2×1: (0,0) undecided — belt (0,1) W→E
// ---------------------------------------------------------------------------
TEST(BeltResources, LaneItem_UndecidedUpstream_Valid) {
    Grid grid(2, 1);
    belt(grid, 0, 1, Direction::West, Direction::East, kEmptyItemId, kIron);
    // (0,0) undecided — upstream OK for WFC

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

// ---------------------------------------------------------------------------
// Belt с item, from слева empty — undecided to не даёт input.
//   grid 2×1: belt (0,0) W→E, (0,1) undecided
// ---------------------------------------------------------------------------
TEST(BeltResources, LaneItem_UndecidedDownstream_Valid) {
    Grid grid(2, 1);
    belt(grid, 0, 0, Direction::West, Direction::East, kEmptyItemId, kIron);
    // (0,1) undecided

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("no input on right side"), std::string::npos) << result.message;
}

// ---------------------------------------------------------------------------
// Прямой belt S→N в (1,1), iron на left — feeders без item, input неоткуда.
//
//       (0,1) undecided
// (1,0) L (1,1) ↑ (1,2) R
//       (2,1) B
// ---------------------------------------------------------------------------
TEST(BeltResources, SideFeeder_MatchingLane_Valid) {
    Grid grid(3, 3);
    belt(grid, 1, 1, Direction::South, Direction::North, kIron, kEmptyItemId);
    belt(grid, 1, 0, Direction::West, Direction::East);
    belt(grid, 1, 2, Direction::East, Direction::West);
    belt(grid, 2, 1, Direction::South, Direction::North);

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("no input on left side"), std::string::npos) << result.message;
}

// ---------------------------------------------------------------------------
// Side feeder mismatch: (0,0) S→N right=iron, side (0,1) copper, (0,2) undecided.
// ---------------------------------------------------------------------------
TEST(BeltResources, SideFeeder_LaneMismatch_Invalid) {
    Grid grid(3, 2);
    belt(grid, 0, 0, Direction::South, Direction::North, kEmptyItemId, kIron);
    belt(grid, 0, 1, Direction::East, Direction::West, kCopper, kEmptyItemId);
    belt(grid, 1, 0, Direction::South, Direction::North);
    // (0,2) undecided

    const ValidationResult result = validate_grid(grid);
    EXPECT_FALSE(result.is_valid);
    EXPECT_NE(result.message.find("Trying to feed"), std::string::npos) << result.message;
}

// ---------------------------------------------------------------------------
// GUI export case:
//   (1,0) W→E left=iron → (1,1) S→N left=iron
//   (2,1) undecided, остальное undecided
// ---------------------------------------------------------------------------
TEST(BeltResources, WestEastIntoSouthNorth_LeftLane_GuiCase) {
    Grid grid(3, 3);
    belt(grid, 1, 0, Direction::West, Direction::East, kIron, kEmptyItemId);
    belt(grid, 1, 1, Direction::South, Direction::North, kIron, kEmptyItemId);
    // (2,1) undecided

    const ValidationResult result = validate_grid(grid);
    EXPECT_TRUE(result.is_valid) << result.message;
}

}  // namespace
}  // namespace fwfc
