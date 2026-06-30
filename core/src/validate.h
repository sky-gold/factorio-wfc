#pragma once

#include "rules/rules.h"
#include "wire/byte_view.h"

#include <cstdint>
#include <string>

namespace fwfc {

ValidationResult validate_snapshot(std::uint32_t width, std::uint32_t height, wire::ByteView cells);

bool load_catalog_bytes(wire::ByteView data, std::string& error);
std::uint32_t wire_format_version();

}  // namespace fwfc
