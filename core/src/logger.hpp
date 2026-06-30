#pragma once

#include <format>
#include <iostream>
#include <string_view>
#include <utility>

namespace fwfc {

template <class... Args>
inline void debug_log(const char* file, int line, std::string_view fmt, Args&&... args) {
    std::cerr << "[DEBUG] " << file << ":" << line << " - "
              << std::vformat(fmt, std::make_format_args(std::forward<Args>(args)...)) << '\n';
}

}  // namespace fwfc

#if defined(FWFC_DEBUG) || defined(_DEBUG)
#define LOG_DEBUG(...) ::fwfc::debug_log(__FILE__, __LINE__, __VA_ARGS__)
#else
#define LOG_DEBUG(...) ((void)0)
#endif
