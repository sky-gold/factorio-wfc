#pragma once

#include "rules/rules.h"

#include <string>
#include <utility>

namespace fwfc::rules_detail {

inline ValidationResult valid() {
    return ValidationResult{true, ""};
}

inline ValidationResult invalid(std::string message) {
    return ValidationResult{false, std::move(message)};
}

}  // namespace fwfc::rules_detail
