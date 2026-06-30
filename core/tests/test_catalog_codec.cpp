#include <gtest/gtest.h>

#include "catalog.h"
#include "wire/catalog_codec.h"
#include "wire/wire_format.h"

#include <array>
#include <cstring>
#include <vector>

namespace fwfc::wire {
namespace {

TEST(CatalogCodecTest, DecodeMinimalCatalog) {
    std::vector<std::uint8_t> blob = {
        'F', 'W', 'F', 'C',  //
        0x01, 0x00,          // version 1
        0x00, 0x00,          // flags
        0x10, 0x00, 0x00, 0x00,  // payload offset 16
        kSectionItems, 0x04, 0x00, 0x00, 0x00,  // section len 4
        0x00, 0x00, 0x00, 0x00,                  // item count 0
    };

    Catalog catalog;
    std::string error;
    ASSERT_TRUE(decode_catalog({blob.data(), blob.size()}, catalog, error)) << error;
    EXPECT_TRUE(catalog.items().empty());
}

TEST(CatalogCodecTest, RejectsBadMagic) {
    std::array<std::uint8_t, kHeaderSize> blob{};
    Catalog catalog;
    std::string error;
    EXPECT_FALSE(decode_catalog({blob.data(), blob.size()}, catalog, error));
    EXPECT_FALSE(error.empty());
}

}  // namespace
}  // namespace fwfc::wire
