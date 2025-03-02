cmake_minimum_required(VERSION 3.10)
project(ThreadManagerModule)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(BUILD_TEST "Build test binary instead of the library" ON)

# Set the path to the include directory
include_directories(${CMAKE_SOURCE_DIR}/include)

# Gather all .cpp files in the src directory
file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/src/*.cpp)
# Gather all .hpp files in the include directory
file(GLOB HEADERS ${CMAKE_SOURCE_DIR}/include/*.hpp)

# Build and install library:
if(NOT BUILD_TEST)
  if(CMAKE_BUILD_TYPE MATCHES "Debug")
    set(CMAKE_CXX_FLAGS "-Wall -Werror -fsanitize=address -g")
    message(STATUS "Building library in debug mode")
    # Create the library from source files
    add_library(ThreadManagerModule STATIC ${SOURCES})

    # Specify the output directory for the library
    set_target_properties(
      ThreadManagerModule
      PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/libDebug
                 ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/libDebug)

    # Installation instructions
    install(TARGETS ThreadManagerModule DESTINATION libDebug)

    # Install the header files
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include
    )# e.g., /usr/local/include
  else()
    message(STATUS "Building library in release mode")
    # Create the library from source files
    add_library(ThreadManagerModule STATIC ${SOURCES})

    # Specify the output directory for the library
    set_target_properties(
      ThreadManagerModule
      PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
                 ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)

    # Installation instructions
    install(TARGETS ThreadManagerModule DESTINATION lib)

    # Install the header files
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include)
  endif()
endif()

if(BUILD_TEST)
  set(CMAKE_BUILD_TYPE DEBUG)
  set(CMAKE_CXX_FLAGS "-Wall -Werror -fsanitize=address -g")
  message(STATUS "Building test binary")
  file(GLOB TEST_FILES ${CMAKE_SOURCE_DIR}/testing/*.cpp)
  add_executable(ThreadManagerModuleTest ${TEST_FILES} ${SOURCES})
  # Find OpenCV package
  set_target_properties(
    ThreadManagerModuleTest PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                       ${CMAKE_SOURCE_DIR}/bin)
endif()

if(CMAKE_BUILD_TYPE MATCHES DEBUG)
  message(STATUS "Building in debug mode")
endif(CMAKE_BUILD_TYPE MATCHES DEBUG)
if(CMAKE_BUILD_TYPE MATCHES RELEASE)
  message(STATUS "Building in release mode")
endif(CMAKE_BUILD_TYPE MATCHES RELEASE)
