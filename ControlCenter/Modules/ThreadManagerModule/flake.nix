{
inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils = {
        url = "github:numtide/flake-utils";
        # inputs.system.follows = "systems";
    };
};

outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem
    (system:
    let
        pkgs = import nixpkgs {
            inherit system;
            config.allowUnfree = true;
        };
        libs = [
            pkgs.libcxx
        ];
    in
        with pkgs;
            {
            devShells.default = mkShell {
                nativeBuildInputs = with pkgs; [
                    bashInteractive
                    cmake
                    libgcc
                    libcxx
                    pkg-config
                    gcc
                ];
                buildInputs = with pkgs; [
                ];
                shellHook = ''
                    ./compile.sh release
                '';
                LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
