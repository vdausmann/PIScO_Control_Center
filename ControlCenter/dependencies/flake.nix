{
inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
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
        ];
    in
        with pkgs;
            {
            devShells.default = mkShell {
                nativeBuildInputs = with pkgs; [
                    bashInteractive
                ];
                buildInputs = with pkgs; [
                    (pkgs.python312.withPackages(ps: with ps;[
                        pylint
                        pyside6
                        numpy
                        matplotlib
                        pandas
                        pyyaml
                        psutil
                        fastapi
                        uvicorn
                        pydantic
                        python-multipart
                        requests
                        pyyaml
						websockets
						qasync
						(opencv4.override {enableGtk3 = true;})
						pyqtgraph
						scikit-image
						h5py
                    ]))
                ];
                shellHook = ''
                '';
                LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
