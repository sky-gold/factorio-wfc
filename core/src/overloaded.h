#pragma once

namespace fwfc {

template <class... Ts>
struct overloaded : Ts... {
    using Ts::operator()...;
};

}  // namespace fwfc
