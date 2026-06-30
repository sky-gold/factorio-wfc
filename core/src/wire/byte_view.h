#pragma once

#include <cstddef>
#include <cstdint>

namespace fwfc::wire {

struct ByteView {
    const std::uint8_t* data = nullptr;
    std::size_t size = 0;
};

}  // namespace fwfc::wire
