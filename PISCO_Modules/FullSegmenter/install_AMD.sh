#!/usr/bin/env bash

echo "Installing dependencies..."
cd "$(dirname "$0")"

SYSTEM=$(nix eval --raw --impure --expr "builtins.currentSystem")
echo "Detected system: ${SYSTEM}"

# Build the package and create a proper profile
nix build "./dependenciesAMD#packages.${SYSTEM}.libtorch-rocm" \
    --out-link latest \
    --impure

# Create a simple shell script that sets up the environment
cat > latest-shell.nix << 'EOF'
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.cmake
    pkgs.gcc
    pkgs.rocmPackages.rocm-core
    pkgs.rocmPackages.rocblas
    pkgs.rocmPackages.rocsparse
    pkgs.rocmPackages.hipfft
  ];

  shellHook = ''
    export LIBTORCH_DIR="$(pwd)/latest/lib/cmake/Torch"
    export LD_LIBRARY_PATH="$(pwd)/latest/lib:$LD_LIBRARY_PATH"
    export CPATH="$(pwd)/latest/include:$CPATH"
  '';
}
EOF

echo "Finished building dependencies."
echo "LibTorch installed to: $(pwd)/latest"
echo "Created shell environment in: latest-shell.nix"