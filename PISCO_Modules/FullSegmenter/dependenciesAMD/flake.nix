{
  description = "LibTorch binary with ROCm support (extracted from PyTorch wheel)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";

    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };

    # Use local PyTorch wheel instead of downloading
    pytorchWheelPath = /home/veit/PIScO_dev/torch-2.6.0+rocm6.4.1.git1ded221d-cp312-cp312-linux_x86_64.whl;

  in {
    packages.${system}.libtorch-rocm =
      pkgs.stdenv.mkDerivation rec {
        pname = "libtorch-rocm";
        version = "2.6.0-rocm6.4.1";

        src = pytorchWheelPath;

        nativeBuildInputs = [
          pkgs.unzip
          pkgs.patchelf
          pkgs.python3
        ];

        buildInputs = [
          pkgs.rocmPackages.rocm-core
          pkgs.rocmPackages.rocblas
          pkgs.rocmPackages.rocsparse
          pkgs.rocmPackages.hipfft
        ];

        unpackPhase = ''
          mkdir -p libtorch_extract
          cd libtorch_extract
          unzip -q $src
          cd ..
        '';

        installPhase = ''
          mkdir -p $out/lib/cmake $out/include $out/share/cmake
          
          # Copy libraries to lib subdirectory
          if [ -d libtorch_extract/torch/lib ]; then
            cp -r libtorch_extract/torch/lib/* $out/lib/
          fi
          
          # Copy headers to include subdirectory
          if [ -d libtorch_extract/torch/include ]; then
            cp -r libtorch_extract/torch/include/* $out/include/
          fi
          
          # Copy cmake files to both locations (for compatibility)
          if [ -d libtorch_extract/torch/share/cmake ]; then
            cp -r libtorch_extract/torch/share/cmake/* $out/lib/cmake/
            cp -r libtorch_extract/torch/share/cmake/* $out/share/cmake/
          fi
          
          # Copy other share files (excluding cmake which we already handled)
          if [ -d libtorch_extract/torch/share ]; then
            for item in libtorch_extract/torch/share/*; do
              if [ "$(basename "$item")" != "cmake" ]; then
                cp -r "$item" $out/share/
              fi
            done
          fi
        '';

        postFixup = ''
          echo "Patching RPATHs..."
          find $out/lib -type f \( -name "*.so*" -o -executable \) 2>/dev/null | while read f; do
            patchelf --set-rpath \
              ${pkgs.lib.makeLibraryPath buildInputs}:$out/lib \
              "$f" 2>/dev/null || true
          done
        '';

        meta = with pkgs.lib; {
          description = "LibTorch C++ distribution with ROCm support (from PyTorch wheel)";
          platforms = platforms.linux;
        };
      };

    defaultPackage.${system} = self.packages.${system}.libtorch-rocm;
  };
}