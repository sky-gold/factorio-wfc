#include "wire/catalog_codec.h"

#include "wire/wire_format.h"

#include <cstring>
#include <string>
#include <type_traits>
#include <vector>

namespace fwfc::wire {
namespace {

struct Reader {
    const std::uint8_t* data = nullptr;
    std::size_t total = 0;
    std::size_t pos = 0;

    bool read_bytes(void* dst, std::size_t n, std::string& error) {
        if (pos + n > total) {
            error = "catalog: unexpected end of buffer";
            return false;
        }
        std::memcpy(dst, data + pos, n);
        pos += n;
        return true;
    }

    template <typename T>
    bool read_le(T& value, std::string& error) {
        static_assert(std::is_trivially_copyable_v<T>);
        return read_bytes(&value, sizeof(T), error);
    }

    bool skip(std::size_t n, std::string& error) {
        if (pos + n > total) {
            error = "catalog: unexpected end of buffer";
            return false;
        }
        pos += n;
        return true;
    }
};

bool read_string(Reader& reader, std::string& out, std::string& error) {
    std::uint16_t len = 0;
    if (!reader.read_le(len, error)) {
        return false;
    }
    if (reader.pos + len > reader.total) {
        error = "catalog: invalid string length";
        return false;
    }
    out.assign(reinterpret_cast<const char*>(reader.data + reader.pos), len);
    reader.pos += len;
    return true;
}

bool decode_items(Reader& reader, std::uint32_t section_len, Catalog& out, std::string& error) {
    const std::size_t end = reader.pos + section_len;
    if (end > reader.total) {
        error = "catalog: items section out of range";
        return false;
    }

    std::uint32_t count = 0;
    if (!reader.read_le(count, error)) {
        return false;
    }

    std::vector<std::string> items;
    items.reserve(count);
    for (std::uint32_t i = 0; i < count; ++i) {
        std::string item;
        if (!read_string(reader, item, error)) {
            return false;
        }
        items.push_back(std::move(item));
    }

    if (reader.pos != end) {
        error = "catalog: items section size mismatch";
        return false;
    }

    out.set_items(std::move(items));
    return true;
}

bool decode_recipes(Reader& reader, std::uint32_t section_len, Catalog& out, std::string& error) {
    const std::size_t end = reader.pos + section_len;
    if (end > reader.total) {
        error = "catalog: recipes section out of range";
        return false;
    }

    std::uint32_t count = 0;
    if (!reader.read_le(count, error)) {
        return false;
    }

    std::vector<RecipeDef> recipes;
    recipes.reserve(count);
    for (std::uint32_t i = 0; i < count; ++i) {
        RecipeDef recipe;
        if (!reader.read_le(recipe.machine_item_index, error)) {
            return false;
        }
        if (!reader.read_le(recipe.craft_time, error)) {
            return false;
        }

        std::uint32_t in_count = 0;
        if (!reader.read_le(in_count, error)) {
            return false;
        }
        recipe.inputs.resize(in_count);
        for (std::uint32_t j = 0; j < in_count; ++j) {
            if (!reader.read_le(recipe.inputs[j].item_index, error)) {
                return false;
            }
            if (!reader.read_le(recipe.inputs[j].amount, error)) {
                return false;
            }
        }

        std::uint32_t out_count = 0;
        if (!reader.read_le(out_count, error)) {
            return false;
        }
        recipe.outputs.resize(out_count);
        for (std::uint32_t j = 0; j < out_count; ++j) {
            if (!reader.read_le(recipe.outputs[j].item_index, error)) {
                return false;
            }
            if (!reader.read_le(recipe.outputs[j].amount, error)) {
                return false;
            }
        }

        recipes.push_back(std::move(recipe));
    }

    if (reader.pos != end) {
        error = "catalog: recipes section size mismatch";
        return false;
    }

    out.set_recipes(std::move(recipes));
    return true;
}

bool decode_machines(Reader& reader, std::uint32_t section_len, Catalog& out, std::string& error) {
    const std::size_t end = reader.pos + section_len;
    if (end > reader.total) {
        error = "catalog: machines section out of range";
        return false;
    }

    std::uint32_t count = 0;
    if (!reader.read_le(count, error)) {
        return false;
    }

    std::vector<MachineDef> machines;
    machines.reserve(count);
    for (std::uint32_t i = 0; i < count; ++i) {
        MachineDef machine;
        if (!reader.read_le(machine.item_index, error)) {
            return false;
        }
        if (!reader.read_le(machine.width, error)) {
            return false;
        }
        if (!reader.read_le(machine.height, error)) {
            return false;
        }
        machines.push_back(machine);
    }

    if (reader.pos != end) {
        error = "catalog: machines section size mismatch";
        return false;
    }

    out.set_machines(std::move(machines));
    return true;
}

bool decode_logistics(Reader& reader, std::uint32_t section_len, Catalog& out, std::string& error) {
    const std::size_t end = reader.pos + section_len;
    if (end > reader.total) {
        error = "catalog: logistics section out of range";
        return false;
    }

    LogisticsDef logistics;
    if (!reader.read_le(logistics.belt_speed, error)) {
        return false;
    }
    if (!reader.read_le(logistics.inserter_speed, error)) {
        return false;
    }

    if (reader.pos != end) {
        error = "catalog: logistics section size mismatch";
        return false;
    }

    out.set_logistics(logistics);
    return true;
}

}  // namespace

bool decode_catalog(ByteView data, Catalog& out, std::string& error) {
    if (data.size < kHeaderSize) {
        error = "catalog: buffer too small";
        return false;
    }

    if (std::memcmp(data.data, kMagic, 4) != 0) {
        error = "catalog: invalid magic";
        return false;
    }

    std::uint16_t version = 0;
    std::uint16_t flags = 0;
    std::uint32_t payload_offset = 0;
    std::memcpy(&version, data.data + 4, sizeof(version));
    std::memcpy(&flags, data.data + 6, sizeof(flags));
    std::memcpy(&payload_offset, data.data + 8, sizeof(payload_offset));
    (void)flags;

    if (version != kVersion) {
        error = "catalog: unsupported version";
        return false;
    }
    if (payload_offset < kHeaderSize || payload_offset > data.size) {
        error = "catalog: invalid payload offset";
        return false;
    }

    Catalog decoded;
    Reader reader{data.data + payload_offset, data.size - payload_offset};

    while (reader.pos < reader.total) {
        std::uint8_t section_id = 0;
        std::uint32_t section_len = 0;
        if (!reader.read_le(section_id, error)) {
            return false;
        }
        if (!reader.read_le(section_len, error)) {
            return false;
        }

        switch (section_id) {
            case kSectionItems:
                if (!decode_items(reader, section_len, decoded, error)) {
                    return false;
                }
                break;
            case kSectionRecipes:
                if (!decode_recipes(reader, section_len, decoded, error)) {
                    return false;
                }
                break;
            case kSectionMachines:
                if (!decode_machines(reader, section_len, decoded, error)) {
                    return false;
                }
                break;
            case kSectionLogistics:
                if (!decode_logistics(reader, section_len, decoded, error)) {
                    return false;
                }
                break;
            default:
                if (!reader.skip(section_len, error)) {
                    return false;
                }
                break;
        }
    }

    out = std::move(decoded);
    return true;
}

}  // namespace fwfc::wire
