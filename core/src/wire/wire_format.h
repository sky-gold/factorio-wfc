#pragma once

#include <cstdint>

namespace fwfc::wire {

inline constexpr char kMagic[4] = {'F', 'W', 'F', 'C'};
inline constexpr std::uint16_t kVersion = 1;
inline constexpr std::uint32_t kHeaderSize = 16;

inline constexpr std::size_t kCellStride = 32;
inline constexpr std::uint8_t kCellTagUndecided = 0xFF;
inline constexpr std::uint8_t kCellTagEmpty = 0x00;

inline constexpr std::uint8_t kTypeIdBelt = 10;
inline constexpr std::uint8_t kTypeIdInputBelt = 11;
inline constexpr std::uint8_t kTypeIdOutputBelt = 12;

inline constexpr std::uint8_t kSectionItems = 0x01;
inline constexpr std::uint8_t kSectionRecipes = 0x02;
inline constexpr std::uint8_t kSectionMachines = 0x03;
inline constexpr std::uint8_t kSectionLogistics = 0x04;

}  // namespace fwfc::wire
