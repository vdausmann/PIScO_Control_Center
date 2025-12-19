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
			config.cudaSupport = true;
        };
        libs = [
            pkgs.libcxx
			pkgs.hdf5
			pkgs.libtorch-bin
        ];
    in
        with pkgs;
            {
            devShells.default = mkShell {
                nativeBuildInputs = with pkgs; [
                    bashInteractive
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
                    hdf5
                    (pkgs.python312.withPackages(ps: with ps;[
						(torch.override ({cudaSupport = true;}))
						(opencv4.override {enableGtk3 = true; enableCuda = false;})
						h5py
					]))
					cudatoolkit
					cudaPackages.cuda_nvcc
					cudaPackages.cuda_cudart
					# (libtorch-bin.override ({cudaSupport = true;}))
					libtorch-bin
                ];
                buildInputs = with pkgs; [
                ];
                shellHook = ''
					export CUDA_HOME=${pkgs.cudaPackages.cuda_nvcc}
					export CUDAToolkit_ROOT=${pkgs.cudaPackages.cuda_nvcc}
                '';
                LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath libs}";
            };
        }
    );
}
