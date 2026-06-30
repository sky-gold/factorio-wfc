#include "validate.h"

#include "catalog.h"
#include "grid.h"
#include "wire/catalog_codec.h"
#include "wire/snapshot_codec.h"
#include "wire/wire_format.h"

#include <string>
#include <utility>

namespace fwfc {

namespace {

ValidationResult invalid(std::string message) {
    return ValidationResult{false, std::move(message)};
}

}  // namespace

ValidationResult validate_snapshot(std::uint32_t width, std::uint32_t height, wire::ByteView cells) {
    if (!session_catalog_loaded()) {
        return invalid("catalog not loaded");
    }

    Grid grid(1, 1);
    std::string error;
    if (!wire::decode_snapshot(width, height, cells, grid, error)) {
        return invalid(error);
    }

    return validate_grid(grid);
}

bool load_catalog_bytes(wire::ByteView data, std::string& error) {
    Catalog catalog;
    if (!wire::decode_catalog(data, catalog, error)) {
        return false;
    }
    set_session_catalog(std::move(catalog));
    return true;
}

std::uint32_t wire_format_version() {
    return wire::kVersion;
}

}  // namespace fwfc
