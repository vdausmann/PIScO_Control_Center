cmake_minimum_required(VERSION 3.10)

# Project name
project(BackgroundCorrection LANGUAGES CXX)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Variables for library name and path
set(LIBRARY_NAME BackgroundCorrectionModule)
set(LIBRARY_PATH "../BackgroundCorrectionModule")

# Add the library's cmake configuration path
list(APPEND CMAKE_PREFIX_PATH "${LIBRARY_PATH}/cmake")

# Find the library
find_package(LIBRARY_NAME REQUIRED)

# Automatically find all source files in this project
file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "include/*.hpp")

# Create the executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Include directories for this project
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/include)

# Link the library
target_link_libraries(${PROJECT_NAME} PRIVATE MyLibrary::MyLibrary)

# Output directories
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                                 ${CMAKE_BINARY_DIR}/bin)
