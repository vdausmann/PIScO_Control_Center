#!/usr/bin/env bash
set -euo pipefail

echo "Installing dependencies..."

# Clean old profile
rm -rf ./latest ./latest-*

SYSTEM=$(nix eval --raw --impure --expr "builtins.currentSystem")
echo "Detected system: ${SYSTEM}"

FLAKE="./dependencies#devShells.${SYSTEM}.default"

echo "Creating devShell profile..."
nix develop "$FLAKE" \
    --profile ./latest \
    --command bash -c "exit"

echo "Forcing full dependency closure into the Nix store..."

# Get full closure paths
PATHS=$(nix path-info -r "$FLAKE")

# Realize everything (build/download all dependencies now)
echo "$PATHS" | xargs nix-store --realise

# echo "Verifying offline availability..."
nix develop ./latest --command bash -c "echo 'Online check passed'"
nix develop ./latest --offline --command bash -c "echo 'Offline check passed'"

echo "Finished building dependencies."
