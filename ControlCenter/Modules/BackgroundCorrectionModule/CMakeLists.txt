cmake_minimum_required(VERSION 3.10)
project(BackgroundCorrectionModule)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(BUILD_TEST "Build test binary instead of the library" OFF)

# Find OpenCV package
find_package(OpenCV REQUIRED)

# Set the path to the include directory
include_directories(${OpenCV_INCLUDE_DIRS} ${CMAKE_SOURCE_DIR}/include)

# Gather all .cpp files in the src directory
file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/src/*.cpp)
# Gather all .hpp files in the include directory
file(GLOB HEADERS ${CMAKE_SOURCE_DIR}/include/*.hpp)

# Build and install library:
if(NOT BUILD_TEST)
  if(CMAKE_BUILD_TYPE MATCHES "Debug")
    set(CMAKE_CXX_FLAGS "-Wall -Werror -fsanitize=address -g")
    message(STATUS "Building library in debug mode")
    add_library(BackgroundCorrectionModule STATIC ${SOURCES})
    target_link_libraries(BackgroundCorrectionModule ${OpenCV_LIBS})
    set_target_properties(
      BackgroundCorrectionModule
      PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/libDebug
                 ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/libDebug)
    install(TARGETS BackgroundCorrectionModule DESTINATION libDebug)
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include)
  else()
    message(STATUS "Building library in release mode")
    add_library(BackgroundCorrectionModule STATIC ${SOURCES})
    target_link_libraries(BackgroundCorrectionModule ${OpenCV_LIBS})
    set_target_properties(
      BackgroundCorrectionModule
      PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
                 ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)
    install(TARGETS BackgroundCorrectionModule DESTINATION lib)
    install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include)
  endif()
endif()

if(BUILD_TEST)
  set(CMAKE_BUILD_TYPE DEBUG)
  set(CMAKE_CXX_FLAGS "-Wall -Werror -fsanitize=address -g")
  message(STATUS "Building test binary")
  file(GLOB TEST_FILES ${CMAKE_SOURCE_DIR}/testing/*.cpp)
  add_executable(BackgroundCorrectionModuleTest ${TEST_FILES} ${SOURCES})
  target_link_libraries(BackgroundCorrectionModuleTest ${OpenCV_LIBS})
  # Set the output directory for the test binary
  set_target_properties(
    BackgroundCorrectionModuleTest PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                              ${CMAKE_SOURCE_DIR}/bin)
endif()
