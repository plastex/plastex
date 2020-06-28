## Specification for nix-build

let
  dependencies = import ./misc/dependencies.nix;
in dependencies.buildEnv {
  name = "plastex-development";
  paths = dependencies.packages;
}

### End of file
