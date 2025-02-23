{
inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils = {
        url = "github:numtide/flake-utils";
        inputs.system.follows = "systems";
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
                    (opencv.override ({
                        enableGtk3 = true;
                        enableCuda = false;
                        enableFfmpeg = true;
                        enableUnfree = true;
                    }))
                    bashInteractive
                    libcxx
                    pkg-config
                    gcc
                ];
                buildInputs = with pkgs; [
                ];
                shellHook = ''
                    cmake --no-warn-unused-cli -DCMAKE_EXPORT_COMPILE_COMMANDS:BOOL=TRUE -DCMAKE_BUILD_TYPE:STRING=Release -DCMAKE_C_COMPILER:FILEPATH=`which gcc` -DCMAKE_CXX_COMPILER:FILEPATH=`which g++` -S./ -B./build -G "Unix Makefiles"
                '';
                LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
