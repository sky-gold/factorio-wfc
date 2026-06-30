#include <gtest/gtest.h>

#include "grid.h"
#include "tile.h"

namespace fwfc {
namespace {

TEST(GridTest, DefaultCellsAreUndecided) {
    Grid grid(4, 3);
    EXPECT_EQ(grid.width(), 4u);
    EXPECT_EQ(grid.height(), 3u);
    for (std::size_t x = 0; x < grid.height(); ++x) {
        for (std::size_t y = 0; y < grid.width(); ++y) {
            EXPECT_FALSE(grid.get(x, y).has_value());
        }
    }
}

TEST(GridTest, SetEmptyTile) {
    Grid grid(2, 2);
    grid.set(1, 0, EmptyTile{});
    ASSERT_TRUE(grid.get(1, 0).has_value());
    EXPECT_EQ(get_tile_type(*grid.get(1, 0)), TileType::Empty);
}

TEST(GridTest, SetUndecided) {
    Grid grid(2, 2);
    grid.set(0, 0, EmptyTile{});
    grid.set(0, 0, std::nullopt);
    EXPECT_FALSE(grid.get(0, 0).has_value());
}

TEST(GridTest, OutOfBoundsGetThrows) {
    Grid grid(2, 2);
    EXPECT_THROW(grid.get(2, 0), std::out_of_range);
    EXPECT_THROW(grid.get(0, 2), std::out_of_range);
}

TEST(GridTest, OutOfBoundsSetThrows) {
    Grid grid(2, 2);
    EXPECT_THROW(grid.set(2, 0, EmptyTile{}), std::out_of_range);
}

TEST(GridTest, InBounds) {
    Grid grid(3, 2);
    EXPECT_TRUE(grid.in_bounds(0, 0));
    EXPECT_TRUE(grid.in_bounds(1, 2));
    EXPECT_FALSE(grid.in_bounds(2, 0));
    EXPECT_FALSE(grid.in_bounds(0, 3));
}

}  // namespace
}  // namespace fwfc
