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
        libs = [];
        in
        with pkgs;
        {
        devShells.default = mkShell {
            nativeBuildInputs = with pkgs; [
                (python311.withPackages(ps: with ps;[
                    pyside6
                    numpy
                    matplotlib
                    pandas
                ]))
            ];
            buildInputs = with pkgs; [
            ];
            shellHook = ''
            '';
            };
        }
    );
}
