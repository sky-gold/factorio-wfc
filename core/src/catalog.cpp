#include "catalog.h"

namespace fwfc {

namespace {
Catalog g_catalog;
bool g_loaded = false;
}  // namespace

Catalog& session_catalog() {
    return g_catalog;
}

void set_session_catalog(Catalog catalog) {
    g_catalog = std::move(catalog);
    g_loaded = true;
}

bool session_catalog_loaded() {
    return g_loaded;
}

void reset_session_for_test() {
    g_catalog = Catalog{};
    g_loaded = false;
}

}  // namespace fwfc
