#!/usr/bin/env bash

# Check if an argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <command>"
    exit 1
fi

# Get the input string
input="$1"

# Decide what to do based on the input string
case "$input" in
    "lib")
        cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build -DBUILD_TEST=OFF -G "Unix Makefiles"
        ;;
    "test")
        cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_C_COMPILER:FILEPATH="$(which gcc)" -DCMAKE_INSTALL_PREFIX=install -DCMAKE_CXX_COMPILER:FILEPATH="$(which g++)" -S./ -B./build -DBUILD_TEST=ON -G "Unix Makefiles"
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: lib, test"
        ;;
esac

