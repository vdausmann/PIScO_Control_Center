#!/usr/bin/env bash

MODE="${1:-release}"

case "$MODE" in
    "debug")
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "rm -rf build && mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Debug .. && cd .. && cmake --build build -j8"
        ;;
    "release")
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "rm -rf build && mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && cd .. && cmake --build build -j8"
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: debug, release"
        ;;
esac
