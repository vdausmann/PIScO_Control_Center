#!/usr/bin/env bash

MODE="${1:-release}"

case "$MODE" in
    "debug")
        nix-shell latest-shell.nix \
          --run "rm -rf build && mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Debug .. && cd .. && cmake --build build -j8"
        ;;
    "release")
        nix-shell latest-shell.nix \
          --run "rm -rf build && mkdir -p build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && cd .. && cmake --build build -j8"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Valid commands: debug, release"
        ;;
esac