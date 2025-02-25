cmake_minimum_required(VERSION 3.10)
project(ThreadManagerModule)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g")

option(BUILD_TEST "Build test binary instead of the library" ON)

# Set the path to the include directory
include_directories(${CMAKE_SOURCE_DIR}/include)

# Gather all .cpp files in the src directory
file(GLOB SOURCES ${CMAKE_SOURCE_DIR}/src/*.cpp)
# Gather all .hpp files in the include directory
file(GLOB HEADERS ${CMAKE_SOURCE_DIR}/include/*.hpp)

# Build and install library:
if(NOT BUILD_TEST)
  set(CMAKE_BUILD_TYPE RELEASE)
  message(STATUS "Building library")
  # Create the library from source files
  add_library(ThreadManagerModule STATIC ${SOURCES})

  # Link OpenCV libraries target_link_libraries(BackgroundCorrectionModule
  # ${OpenCV_LIBS})

  # Specify the output directory for the library
  set_target_properties(
    ThreadManagerModule
    PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib
               ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)

  # Installation instructions
  install(TARGETS ThreadManagerModule
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
