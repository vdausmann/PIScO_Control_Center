cmake_minimum_required(VERSION 3.15)
project(BackgroundCorrectionModule)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_BUILD_TYPE Release)

find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

set(SRCDIR src)
file(GLOB SOURCE_FILES "${SRCDIR}/*.cpp")
file(GLOB HEADER_FILES "${SRCDIR}/*.hpp")

message(STATUS "OpenCV library status:")
message(STATUS "    config: ${OpenCV_DIR}")
message(STATUS "    version: ${OpenCV_VERSION}")
message(STATUS "    libraries: ${OpenCV_LIBS}")
message(STATUS "    include path: ${OpenCV_INCLUDE_DIRS}")

add_library("${PROJECT_NAME}Lib" STATIC ${SOURCE_FILES} ${HEADER_FILES})
target_link_libraries("${PROJECT_NAME}Lib" ${OpenCV_LIBS})

add_executable(${PROJECT_NAME} ${SOURCE_FILES})
target_link_libraries(${PROJECT_NAME} "${PROJECT_NAME}Lib" ${OpenCV_LIBS})

# installation
set(LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(EXECUTABLE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Installation paths
set(INSTALL_INCLUDE_DIR ${CMAKE_BINARY_DIR}/"${PROJECT_NAME}Lib"/include)
set(INSTALL_LIB_DIR ${CMAKE_BINARY_DIR}/"${PROJECT_NAME}Lib"/lib)

# Install headers
install(FILES ${HEADER_FILES} DESTINATION ${INSTALL_INCLUDE_DIR})

# Install library
install(TARGETS "${PROJECT_NAME}Lib" ARCHIVE DESTINATION ${INSTALL_LIB_DIR})

# Install executable (optional)
install(TARGETS ${PROJECT_NAME} RUNTIME DESTINATION ${CMAKE_BINARY_DIR}/bin)

# Ensure directories are created
add_custom_target(
  prepare_structure ALL
  COMMAND ${CMAKE_COMMAND} -E make_directory ${INSTALL_INCLUDE_DIR}
  COMMAND ${CMAKE_COMMAND} -E make_directory ${INSTALL_LIB_DIR})

# Make library depend on the directory structure
add_dependencies("${PROJECT_NAME}Lib" prepare_structure)
