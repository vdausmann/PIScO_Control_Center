#!/usr/bin/env bash

MODE="${1:-release}"
SETTINGS="${2:-settings.cfg}"


case "$MODE" in
    "debug")
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "./binDebug/Segmenter $SETTINGS"
        ;;
    "release")
		nix develop ./latest \
		  --offline \
		  --no-update-lock-file \
		  --command bash -c \
		  "./bin/Segmenter $SETTINGS"
        ;;
    *)
        echo "Unknown command: $input"
        echo "Valid commands: debug, release"
        ;;
esac
