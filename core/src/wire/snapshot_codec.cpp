#include "wire/snapshot_codec.h"

#include "tile.h"
#include "wire/wire_format.h"

#include <cstring>

namespace fwfc::wire {

namespace {

std::uint32_t read_u32_le(const std::uint8_t* data) {
    std::uint32_t value = 0;
    std::memcpy(&value, data, sizeof(value));
    return value;
}

double read_f64_le(const std::uint8_t* data) {
    double value = 0.0;
    std::memcpy(&value, data, sizeof(value));
    return value;
}

bool is_valid_direction(std::uint8_t value) { return value <= static_cast<std::uint8_t>(Direction::West); }

}  // namespace

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
    for (std::uint32_t x = 0; x < height; ++x) {
        for (std::uint32_t y = 0; y < width; ++y) {
            const std::size_t offset = (static_cast<std::size_t>(x) * width + y) * kCellStride;
            const std::uint8_t tag = cells.data[offset];

            if (tag == kCellTagUndecided) {
                grid.set(x, y, std::nullopt);
                continue;
            }
            if (tag == kCellTagEmpty) {
                grid.set(x, y, EmptyTile{});
                continue;
            }
            if (tag == kTypeIdBelt) {
                const std::uint8_t from_dir_raw = cells.data[offset + 1];
                const std::uint8_t to_dir_raw = cells.data[offset + 2];
                if (!is_valid_direction(from_dir_raw) || !is_valid_direction(to_dir_raw)) {
                    error = "snapshot: invalid belt direction";
                    return false;
                }

                BeltTile belt;
                belt.from_dir = static_cast<Direction>(from_dir_raw);
                belt.to_dir = static_cast<Direction>(to_dir_raw);
                belt.left_item_id = read_u32_le(cells.data + offset + 4);
                belt.right_item_id = read_u32_le(cells.data + offset + 8);
                grid.set(x, y, belt);
                continue;
            }
            if (tag == kTypeIdInputBelt) {
                const std::uint8_t to_dir_raw = cells.data[offset + 1];
                if (!is_valid_direction(to_dir_raw)) {
                    error = "snapshot: invalid input belt direction";
                    return false;
                }

                InputBeltTile input_belt;
                input_belt.to_dir = static_cast<Direction>(to_dir_raw);
                input_belt.left_item_id = read_u32_le(cells.data + offset + 4);
                input_belt.right_item_id = read_u32_le(cells.data + offset + 8);
                input_belt.left_max_rate = read_f64_le(cells.data + offset + 12);
                input_belt.right_max_rate = read_f64_le(cells.data + offset + 20);
                grid.set(x, y, input_belt);
                continue;
            }
            if (tag == kTypeIdOutputBelt) {
                const std::uint8_t from_dir_raw = cells.data[offset + 1];
                if (!is_valid_direction(from_dir_raw)) {
                    error = "snapshot: invalid output belt direction";
                    return false;
                }

                OutputBeltTile output_belt;
                output_belt.from_dir = static_cast<Direction>(from_dir_raw);
                output_belt.left_item_id = read_u32_le(cells.data + offset + 4);
                output_belt.right_item_id = read_u32_le(cells.data + offset + 8);
                output_belt.left_min_rate = read_f64_le(cells.data + offset + 12);
                output_belt.right_min_rate = read_f64_le(cells.data + offset + 20);
                grid.set(x, y, output_belt);
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
