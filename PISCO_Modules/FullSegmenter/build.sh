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
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Debug .. && cd .. && cmake --build build"
        ;;
    "release")
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && cd .. && cmake --build build"
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: debug, release"
        ;;
esac
