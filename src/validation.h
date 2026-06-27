#pragma once

#include "grid.h"
#include "wire/byte_view.h"

#include <cstdint>
#include <string>

namespace fwfc {

struct ValidationResult {
    bool is_valid = true;
    std::string message;
};

ValidationResult validate_grid(const Grid& grid);

ValidationResult validate_snapshot(std::uint32_t width,
                                   std::uint32_t height,
                                   wire::ByteView cells);

bool load_catalog_bytes(wire::ByteView data, std::string& error);

std::uint32_t wire_format_version();

}  // namespace fwfc
