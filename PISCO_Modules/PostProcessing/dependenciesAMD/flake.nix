{
  description = "LibTorch binary with ROCm support (based on libtorch-bin)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";

    pkgs = import nixpkgs {
      inherit system;
      config.allowUnfree = true;
    };

    # ---- CONFIG ----
    pytorchVersion = "2.1.2";
    rocmVersion = "5.7";  # MUST match your system ROCm
    # ----------------

    libtorchUrl =
      "https://download.pytorch.org/libtorch/rocm${rocmVersion}/"
      + "libtorch-cxx11-abi-shared-with-deps-${pytorchVersion}%2Brocm${rocmVersion}.zip";

  in {
    packages.${system}.libtorch-rocm =
      pkgs.stdenv.mkDerivation rec {
        pname = "libtorch-rocm";
        version = "${pytorchVersion}-rocm${rocmVersion}";

        src = pkgs.fetchurl {
          url = libtorchUrl;
          # ⚠️ Run once with fake hash, then replace
          sha256 = "sha256-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=";
        };

        nativeBuildInputs = [
          pkgs.unzip
          pkgs.patchelf
        ];

        buildInputs = with pkgs.rocmPackages; [
          rocm-runtime
          hip
          rocblas
          miopen
          hipsparse
          rocsparse
          hipfft
        ];

        unpackPhase = ''
          unzip $src
        '';

        installPhase = ''
          mkdir -p $out
          cp -r libtorch/* $out/
        '';

        postFixup = ''
          echo "Patching RPATHs..."
          find $out -type f -executable | while read f; do
            patchelf --set-rpath \
              ${pkgs.lib.makeLibraryPath buildInputs}:$out/lib \
              "$f" || true
          done
        '';

        meta = with pkgs.lib; {
          description = "LibTorch C++ distribution with ROCm support";
          platforms = platforms.linux;
        };
      };

    # Convenience alias
    defaultPackage.${system} = self.packages.${system}.libtorch-rocm;
  };
}
