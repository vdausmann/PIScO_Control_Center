#!/usr/bin/env bash

if [  "${1}" '=' "debug" ]; then
    RUN_DIR="binDebug"
    shift  
elif [  "${1}" '=' "release" ]; then
    RUN_DIR="bin"
    shift  
else
    RUN_DIR="bin"
fi

FILE=$(find $RUN_DIR -maxdepth 1 -type f | head -n 1)

echo "Running: " "$FILE" "$@"
if [ -f ".direnv" ]; then
    "./$FILE $@"
else
    nix develop --command bash -c "./$FILE $@"
fi
