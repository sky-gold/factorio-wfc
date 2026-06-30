cmake_minimum_required(VERSION 3.15)
project(factorio_wfc VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

enable_testing()

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

include(FetchContent)

FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/heads/main.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

set(PYBIND11_FINDPYTHON ON)
FetchContent_Declare(
    pybind11
    URL https://github.com/pybind/pybind11/archive/refs/heads/master.zip
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(pybind11)

add_subdirectory(core/src)
add_subdirectory(core/tests)
