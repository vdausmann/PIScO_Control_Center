{
inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
};
outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem
    (system:
    let
        pkgs = import nixpkgs {
            inherit system;
        };
        libs = [
            pkgs.libcxx
        ];
        in
        with pkgs;
        {
        devShells.default = mkShell {
            nativeBuildInputs = with pkgs; [
                (opencv.override ({
                    enableGtk3 = true;
                    enableCuda = false;
                    enableFfmpeg = true;
                    enableUnfree = true;
                }))
                cmake
                libgcc
                libcxx
                pkg-config
                gcc
            ];
            buildInputs = with pkgs; [
            ];
            shellHook = ''
            '';
            LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
