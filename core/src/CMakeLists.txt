# Библиотека из всех .cpp, кроме bindings.cpp (pybind entry point — аналог main.cpp в yahtzee-solver)
# RELATIVE: пути как в yahtzee (bindings.cpp), иначе list(REMOVE_ITEM) на Windows не срабатывает
file(GLOB_RECURSE LIB_SOURCES CONFIGURE_DEPENDS
    RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
    "*.cpp"
)
set(BINDINGS_CPP "bindings.cpp")
list(REMOVE_ITEM LIB_SOURCES "${BINDINGS_CPP}")

add_library(factorio_wfc_lib STATIC ${LIB_SOURCES})

target_include_directories(factorio_wfc_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

if(MSVC)
    target_compile_options(factorio_wfc_lib PRIVATE /W4)
else()
    target_compile_options(factorio_wfc_lib PRIVATE -Wall -Wextra)
endif()

pybind11_add_module(_factorio_wfc "${CMAKE_CURRENT_SOURCE_DIR}/${BINDINGS_CPP}")
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
