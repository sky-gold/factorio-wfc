#pragma once

#include "grid.h"
#include "wire/byte_view.h"

#include <cstdint>
#include <string>

namespace fwfc::wire {

bool decode_snapshot(std::uint32_t width,
                     std::uint32_t height,
                     ByteView cells,
                     Grid& out,
                     std::string& error);

}  // namespace fwfc::wire
