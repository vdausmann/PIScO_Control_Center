#!/usr/bin/env bash


# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <command>"
    exit 1
fi

# Get the input string
input="$1"

case "$input" in
    "debug")
        cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build -DBUILD_PROFILING=OFF
        ;;
    "release")
        cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build -DBUILD_PROFILING=OFF
        ;;
    "profiling")
        cmake -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build -DBUILD_PROFILING=ON
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: debug, release"
        ;;
esac
