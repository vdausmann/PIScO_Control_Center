#!/usr/bin/env bash

MODE="${1:-release}"
SETTINGS="${2:-settings.cfg}"

case "$MODE" in
    "debug")
        nix-shell latest-shell.nix \
          --run "./binDebug/Segmenter $SETTINGS"
        ;;
    "release")
        nix-shell latest-shell.nix \
          --run "./bin/Segmenter $SETTINGS"
        ;;
    *)
        echo "Unknown command: $MODE"
        echo "Valid commands: debug, release"
        ;;
esac