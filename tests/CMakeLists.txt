file(GLOB TEST_SOURCES "*.cpp")

add_executable(runTests ${TEST_SOURCES})

target_link_libraries(runTests PRIVATE factorio_wfc_lib gtest_main)

target_include_directories(runTests PRIVATE ${CMAKE_SOURCE_DIR}/src)

set_target_properties(runTests PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/$<CONFIG>"
)

add_test(NAME AllTests COMMAND runTests)
