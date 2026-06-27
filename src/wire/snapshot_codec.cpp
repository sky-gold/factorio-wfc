#include "wire/snapshot_codec.h"

#include "tile.h"
#include "wire/wire_format.h"

namespace fwfc::wire {

bool decode_snapshot(std::uint32_t width,
                     std::uint32_t height,
                     ByteView cells,
                     Grid& out,
                     std::string& error) {
    if (width == 0 || height == 0) {
        error = "snapshot: invalid grid size";
        return false;
    }

    const std::size_t expected = static_cast<std::size_t>(width) * height * kCellStride;
    if (cells.size != expected) {
        error = "snapshot: cells buffer size mismatch";
        return false;
    }

    Grid grid(width, height);
    for (std::uint32_t y = 0; y < height; ++y) {
        for (std::uint32_t x = 0; x < width; ++x) {
            const std::size_t offset = (static_cast<std::size_t>(y) * width + x) * kCellStride;
            const std::uint8_t tag = cells.data[offset];

            if (tag == kCellTagUndecided) {
                grid.set(x, y, std::nullopt);
                continue;
            }
            if (tag == kCellTagEmpty) {
                grid.set(x, y, EmptyTile{});
                continue;
            }

            error = "snapshot: unsupported tile type in wire v1 scaffold";
            return false;
        }
    }

    out = std::move(grid);
    return true;
}

}  // namespace fwfc::wire
