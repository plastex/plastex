### Install the project in development mode

let
  dependencies = import ./misc/dependencies.nix;
in dependencies.buildPythonPackage {
  name = "plastex";
  src = ./..;
  doCheck = false;
  propagatedBuildInputs = dependencies.packages;
}

### End of file
