#!/usr/bin/env bash

echo "Installing dependencies..."
rm latest*
SYSTEM=$(nix eval --raw --impure --expr "builtins.currentSystem")
echo "Detected system: ${SYSTEM}"
nix develop "./dependencies#devShells.${SYSTEM}.default" --profile ./latest --command bash -c "exit"
echo "Finished building dependencies."
