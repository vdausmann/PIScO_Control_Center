#!/usr/bin/env bash

SETTINGS=$1
echo "Using settings from" $SETTINGS

nix develop ./latest \
    --offline \
    --no-update-lock-file \
    --command bash -c \
    "./bin/Segmenter $SETTINGS"
