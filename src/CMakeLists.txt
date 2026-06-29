add_library(factorio_wfc_lib STATIC
    cell.cpp
    tile.cpp
    grid.cpp
    catalog.cpp
    validation.cpp
    wire/catalog_codec.cpp
    wire/snapshot_codec.cpp
)

target_include_directories(factorio_wfc_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

if(MSVC)
    target_compile_options(factorio_wfc_lib PRIVATE /W4)
else()
    target_compile_options(factorio_wfc_lib PRIVATE -Wall -Wextra)
endif()

pybind11_add_module(_factorio_wfc bindings.cpp)
target_link_libraries(_factorio_wfc PRIVATE factorio_wfc_lib)

if(MSVC)
    target_compile_options(_factorio_wfc PRIVATE /W4)
else()
    target_compile_options(_factorio_wfc PRIVATE -Wall -Wextra)
endif()

set_target_properties(_factorio_wfc PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
)
