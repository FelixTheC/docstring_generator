cmake_minimum_required(VERSION 3.24)
project(src VERSION 1.0 LANGUAGES CXX)

if ("$ENV{TESTING}")
    enable_testing()

    include(FetchContent)
    FetchContent_Declare(
            googletest
            URL https://github.com/google/googletest/archive/refs/tags/release-1.12.1.zip
    )

    FetchContent_MakeAvailable(googletest)
    include_directories(${GTEST_INCLUDE_DIRS})

    add_executable(src main.cpp)
    target_link_libraries(src gtest_main)

    include(GoogleTest)

else ()
    find_package(Python 3.10 COMPONENTS Interpreter Development REQUIRED)
    add_subdirectory(extern/pybind11)

    add_executable(src main.cpp docstringFormat.hpp)
    pybind11_add_module(src example.cpp)

    target_link_libraries(src PRIVATE pybind11::module pybind11::lto pybind11::windows_extras)
endif ()


if ("$ENV{GCC}")
    target_compile_options(src PRIVATE
            -Wall
            -Wextra
            -Werror
            -Wpedantic
            -Wshadow
            -Wnon-virtual-dtor
            -Wold-style-cast
            -Wcast-align
            -Wfloat-conversion
            -fno-omit-frame-pointer
            -fsanitize=address
            )
    target_link_options(src PRIVATE -fsanitize=address)
endif ()

target_compile_features(src PUBLIC cxx_std_20)
set_target_properties(src PROPERTIES
        CXX_STANDARD 20
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO)