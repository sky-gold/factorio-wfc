#pragma once

#include "catalog.h"
#include "wire/byte_view.h"

#include <string>

namespace fwfc::wire {

bool decode_catalog(ByteView data, Catalog& out, std::string& error);

}  // namespace fwfc::wire
