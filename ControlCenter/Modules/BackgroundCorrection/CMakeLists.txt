cmake_minimum_required(VERSION 3.10)
project(BackgroundCorrection)

set(CMAKE_CXX_STANDARD 23) # Specify C++ standard version
set(CMAKE_CXX_STANDARD_REQUIRED ON) # Ensure the chosen version is used
set(CMAKE_BUILD_TYPE Release)
# set(CMAKE_CXX_EXTENSIONS OFF) # Disable compiler-specific extensions
# (optional)

# Variable for the project name
set(PROJECT_NAME "BackgroundCorrection")

# Print the project name and C++ version being used
message(STATUS "Configuring ${PROJECT_NAME} with C++ ${CMAKE_CXX_STANDARD}...")

# Specify the directory where the BackgroundCorrectionModule is installed
set(BG_CORRECTION_MODULE_DIR "../BackgroundCorrectionModule")
# Check if BackgroundCorrectionModule is available
if(EXISTS ${BG_CORRECTION_MODULE_DIR}/lib/libBackgroundCorrectionModule.a
   OR EXISTS ${BG_CORRECTION_MODULE_DIR}/lib/libBackgroundCorrectionModule.so)
  message(
    STATUS "Found BackgroundCorrectionModule at ${BG_CORRECTION_MODULE_DIR}")
else()
  message(
    FATAL_ERROR
      "BackgroundCorrectionModule library not found in ${BG_CORRECTION_MODULE_DIR}. Please check the installation."
  )
endif()

# Specify the directory where the ThreadManagerModule is installed
set(THREAD_MANAGER_MODULE_DIR "../ThreadManagerModule/")
# Check if ThreadManagerModule is available
if(EXISTS ${THREAD_MANAGER_MODULE_DIR}/lib/libThreadManagerModule.a
   OR EXISTS ${THREAD_MANAGER_MODULE_DIR}/lib/libThreadManagerModule.so)
  message(STATUS "Found ThreadManagerModule at ${THREAD_MANAGER_MODULE_DIR}")
else()
  message(
    FATAL_ERROR
      "ThreadManagerModule library not found in ${THREAD_MANAGER_MODULE_DIR}. Please check the installation."
  )
endif()

# Add OpenCV support
find_package(OpenCV REQUIRED)

# Check if OpenCV is found
if(OpenCV_FOUND)
  message(STATUS "OpenCV found at ${OpenCV_DIR}")
else()
  message(FATAL_ERROR "OpenCV not found. Please install OpenCV and try again.")
endif()

# Add the path to the include directory for BackgroundCorrectionModule
include_directories(${BG_CORRECTION_MODULE_DIR}/include)
# Add the path to the library directory for BackgroundCorrectionModule
link_directories(${BG_CORRECTION_MODULE_DIR}/lib)

# Same for ThreadManagerModule
include_directories(${THREAD_MANAGER_MODULE_DIR}/include)
# Add the path to the library directory for BackgroundCorrectionModule
link_directories(${THREAD_MANAGER_MODULE_DIR}/lib)

# Automatically detect all source and header files
file(GLOB SRC_FILES ${CMAKE_SOURCE_DIR}/src/*.cpp) # Collect all .cpp files in
                                                   # the src directory
file(GLOB HEADER_FILES ${CMAKE_SOURCE_DIR}/include/*.hpp) # Collect all .hpp
                                                          # files in the include
                                                          # directory

# Add your source files (automatically detected)
add_executable(${PROJECT_NAME} ${SRC_FILES})

# Link the BackgroundCorrectionModule library and OpenCV libraries
target_link_libraries(${PROJECT_NAME} BackgroundCorrectionModule
                      ThreadManagerModule ${OpenCV_LIBS})

# Set the output directory for the binary to a 'bin' folder next to 'src'
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY
                                                 ${CMAKE_SOURCE_DIR}/bin)

# Check if the executable was created successfully
message(
  STATUS
    "Executable ${PROJECT_NAME} created successfully in ${CMAKE_SOURCE_DIR}/bin."
)
