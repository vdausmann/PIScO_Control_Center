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
  set(CMAKE_BUILD_TYPE RELEASE)
  message(STATUS "Building library")
  # Create the library from source files
  add_library(BackgroundCorrectionModule STATIC ${SOURCES})

  # Link OpenCV libraries
  target_link_libraries(BackgroundCorrectionModule ${OpenCV_LIBS})

  # Specify the output directory for the library
  set_target_properties(
    BackgroundCorrectionModule
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
               ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)

  # Installation instructions
  install(TARGETS BackgroundCorrectionModule
          DESTINATION lib # Where the library will go (e.g., /usr/local/lib or
                          # /path/to/install/lib)
  )

  # Install the header files
  install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/ DESTINATION include
  )# e.g., /usr/local/include
endif()

if(BUILD_TEST)
  set(CMAKE_BUILD_TYPE DEBUG)
  message(STATUS "Building test binary")
  file(GLOB TEST_FILES ${CMAKE_SOURCE_DIR}/testing/*.cpp)
  add_executable(BackgroundCorrectionModuleTest ${TEST_FILES} ${SOURCES})
  target_link_libraries(BackgroundCorrectionModuleTest ${OpenCV_LIBS})
  # Set the output directory for the test binary
  set_target_properties(
    BackgroundCorrectionModuleTest PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                              ${CMAKE_SOURCE_DIR}/bin)
endif()

if(CMAKE_BUILD_TYPE MATCHES DEBUG)
  message(STATUS "Building in debug mode")
endif(CMAKE_BUILD_TYPE MATCHES DEBUG)
if(CMAKE_BUILD_TYPE MATCHES RELEASE)
  message(STATUS "Building in release mode")
endif(CMAKE_BUILD_TYPE MATCHES RELEASE)
