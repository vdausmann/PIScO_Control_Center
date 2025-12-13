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
        cmake -DCMAKE_BUILD_TYPE=Debug 
        ;;
    "release")
        cmake -DCMAKE_BUILD_TYPE=Release 
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: debug, release"
        ;;
esac
