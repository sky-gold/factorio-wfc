#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace fwfc {

struct RecipeIngredient {
    std::uint32_t item_index = 0;
    double amount = 0.0;
};

struct RecipeDef {
    std::uint32_t machine_item_index = 0;
    double craft_time = 0.0;
    std::vector<RecipeIngredient> inputs;
    std::vector<RecipeIngredient> outputs;
};

struct MachineDef {
    std::uint32_t item_index = 0;
    std::uint32_t width = 1;
    std::uint32_t height = 1;
};

struct LogisticsDef {
    double belt_speed = 0.0;
    double inserter_speed = 0.0;
};

class Catalog {
public:
    const std::vector<std::string>& items() const { return items_; }
    const std::vector<RecipeDef>& recipes() const { return recipes_; }
    const std::vector<MachineDef>& machines() const { return machines_; }
    const LogisticsDef& logistics() const { return logistics_; }

    void set_items(std::vector<std::string> items) { items_ = std::move(items); }
    void set_recipes(std::vector<RecipeDef> recipes) { recipes_ = std::move(recipes); }
    void set_machines(std::vector<MachineDef> machines) { machines_ = std::move(machines); }
    void set_logistics(LogisticsDef logistics) { logistics_ = logistics; }

private:
    std::vector<std::string> items_;
    std::vector<RecipeDef> recipes_;
    std::vector<MachineDef> machines_;
    LogisticsDef logistics_;
};

Catalog& session_catalog();
void set_session_catalog(Catalog catalog);
bool session_catalog_loaded();
void reset_session_for_test();

}  // namespace fwfc
