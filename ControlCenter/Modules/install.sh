#!/usr/bin/env bash

# Check if Nix is installed
if ! command -v nix &>/dev/null; then
    echo "Error: Nix is not installed. Please install Nix before running this script."
    exit 1
fi

# Find all module directories (assuming each module has a flake.nix file)
MODULES=("ThreadManagerModule" "BackgroundCorrectionModule" "SegmenterParallel")

COMPILE_ARG="${1:-release}"

# Compile modules in order
for module in "${MODULES[@]}"; do
    if [ -d "$module" ] && [ -f "$module/flake.nix" ]; then
        echo "Entering module: $module"
        cd "$module" || { echo "Failed to enter $module"; exit 1; }

        # Enter Nix shell and compile the module
        nix develop --command bash -c "./compile.sh $COMPILE_ARG && cmake --build build"

        # Return to the root directory
        cd - >/dev/null || exit
    else
        echo "Skipping $module: Directory or flake.nix not found."
    fi
    echo "-----------------------------------------------------"
done
