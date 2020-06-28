### Specification for nix-shell

let
  dependencies = import ./misc/dependencies.nix;
in dependencies.mkShell {
  buildInputs = dependencies.packages;
}

### End of file
