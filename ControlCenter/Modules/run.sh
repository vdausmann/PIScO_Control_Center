#!/usr/bin/env bash

# Define the list of modules
MODULES=("SegmenterParallel")  # Replace with actual module names

# Check if a module name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <module_name> [additional_arguments...]"
    exit 1
fi

MODULE_NAME="$1"
shift  # Remove the first argument (module name) so that $@ contains only additional arguments

# Check if the module exists
if [[ ! " ${MODULES[@]} " =~ " ${MODULE_NAME} " ]]; then
    echo "Error: Unknown module '$MODULE_NAME'. Available modules: ${MODULES[*]}"
    exit 1
fi

# Check if the module directory exists
if [ ! -d "$MODULE_NAME" ]; then
    echo "Error: Directory for module '$MODULE_NAME' not found."
    exit 1
fi

echo "Running module: $MODULE_NAME with arguments: $@"

# Change to module directory and execute the module with additional arguments
{
    cd "$MODULE_NAME" || exit 1
    # Run the module inside Nix shell
    "./run.sh $@"
}

