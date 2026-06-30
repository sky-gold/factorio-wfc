#include <gtest/gtest.h>

#include "grid.h"
#include "tile.h"
#include "types.h"
#include "rules/rules.h"

namespace fwfc {
namespace {

Grid empty_grid_3x3() {
    Grid grid(3, 3);
    for (std::size_t x = 0; x < 3; ++x) {
        for (std::size_t y = 0; y < 3; ++y) {
            grid.set(x, y, EmptyTile{});
        }
    }
    return grid;
}

void belt(Grid& grid, std::size_t x, std::size_t y, Direction from_dir, Direction to_dir) {
    BeltTile b;
    b.from_dir = from_dir;
    b.to_dir = to_dir;
    grid.set(x, y, b);
}

// ---------------------------------------------------------------------------
// Straight S→N в (1,1). Перебор bottom × left × right (8 комбинаций).
//
//       (0,1) .
// (1,0) L (1,1) ↑ (1,2) R
//       (2,1) B
//
// L = (1,0) W→E,  R = (1,2) E→W,  B = (2,1) S→N (если флаг = 1)
// ---------------------------------------------------------------------------
TEST(BeltTopology, StraightUp_8Combinations) {
    for (bool bottom : {false, true}) {
        for (bool left : {false, true}) {
            for (bool right : {false, true}) {
                Grid grid = empty_grid_3x3();
                belt(grid, 1, 1, Direction::South, Direction::North);
                if (bottom) {
                    belt(grid, 2, 1, Direction::South, Direction::North);
                }
                if (left) {
                    belt(grid, 1, 0, Direction::West, Direction::East);
                }
                if (right) {
                    belt(grid, 1, 2, Direction::East, Direction::West);
                }

                const bool expect_valid =
                    bottom || (left && right) || (!left && !right);
                const ValidationResult result = validate_grid(grid);

                SCOPED_TRACE("bottom=" + std::to_string(bottom) + " left=" + std::to_string(left) +
                             " right=" + std::to_string(right));
                EXPECT_EQ(result.is_valid, expect_valid) << result.message;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Corner W→N в (1,1). Перебор left × right × bottom (8 комбинаций).
//
//       (0,1) .
// (1,0) L (1,1)⌐ (1,2) R
//       (2,1) B
//
// L = (1,0) W→E,  R = (1,2) E→W,  B = (2,1) S→N
//
// Truth table (L, R, B → valid):
//   0,0,0→0  0,0,1→0  0,1,0→1  0,1,1→0
//   1,0,0→0  1,0,1→0  1,1,0→0  1,1,1→0
// ---------------------------------------------------------------------------
TEST(BeltTopology, CurveWestNorth_8Combinations) {
    for (bool left : {false, true}) {
        for (bool right : {false, true}) {
            for (bool bottom : {false, true}) {
                Grid grid = empty_grid_3x3();
                belt(grid, 1, 1, Direction::West, Direction::North);
                if (left) {
                    belt(grid, 1, 0, Direction::West, Direction::East);
                }
                if (right) {
                    belt(grid, 1, 2, Direction::East, Direction::West);
                }
                if (bottom) {
                    belt(grid, 2, 1, Direction::South, Direction::North);
                }

                bool expect_valid = false;
                if (left && !right && !bottom) {
                    expect_valid = true;
                }

                const ValidationResult result = validate_grid(grid);

                SCOPED_TRACE("left=" + std::to_string(left) + " right=" + std::to_string(right) +
                             " bottom=" + std::to_string(bottom));
                EXPECT_EQ(result.is_valid, expect_valid) << result.message;
            }
        }
    }
}


// ---------------------------------------------------------------------------
// Corner E→N в (1,1). Перебор left × right × bottom (8 комбинаций).
//
//       (0,1) .
// (1,0) L (1,1)⌐ (1,2) R
//       (2,1) B
//
// Truth table (L, R, B → valid):
//   0,0,0→0  0,0,1→1  0,1,0→0  0,1,1→0
//   1,0,0→0  1,0,1→0  1,1,0→0  1,1,1→0
// ---------------------------------------------------------------------------
TEST(BeltTopology, CurveEastNorth_8Combinations) {
    for (bool left : {false, true}) {
        for (bool right : {false, true}) {
            for (bool bottom : {false, true}) {
                Grid grid = empty_grid_3x3();
                belt(grid, 1, 1, Direction::East, Direction::North);
                if (left) {
                    belt(grid, 1, 0, Direction::West, Direction::East);
                }
                if (right) {
                    belt(grid, 1, 2, Direction::East, Direction::West);
                }
                if (bottom) {
                    belt(grid, 2, 1, Direction::South, Direction::North);
                }

                bool expect_valid = false;
                if (!left && right && !bottom) {
                    expect_valid = true;
                }

                const ValidationResult result = validate_grid(grid);

                SCOPED_TRACE("left=" + std::to_string(left) + " right=" + std::to_string(right) +
                             " bottom=" + std::to_string(bottom));
                EXPECT_EQ(result.is_valid, expect_valid) << result.message;
            }
        }
    }
}

}  // namespace
}  // namespace fwfc
