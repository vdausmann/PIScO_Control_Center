#!/usr/bin/env bash

# Check if Nix is installed
if ! command -v nix &>/dev/null; then
    echo "Error: Nix is not installed. Please install Nix before running this script."
    exit 1
fi

# Find all module directories (assuming each module has a flake.nix file)
MODULES=("ThreadManagerModule" "BackgroundCorrectionModule" "SegmenterParallel")

# Loop through each module and build it
for module in $MODULES; do
    echo "Entering module: $module"
    echo "-----------------------------------------------------"
    cd "$module" || { echo "Failed to enter $module"; exit 1; }

    # Enter Nix shell and compile the module
    nix develop --command bash -c "./compile.sh release"

    # Return to the root directory
    cd - >/dev/null || exit
    echo "Finished compiling module: $module"
    echo "-----------------------------------------------------"
done

echo "All modules compiled successfully."

