### Project development dependencies

let
  distributions = import ./distributions.nix;
  nixpkgs = import distributions.nixpkgsPath {};
  python = nixpkgs.python38;
  nixPython = import distributions.nixPythonPath {
    inherit nixpkgs python;
  };
  pythonEnvironment = python.withPackages (
    packages:
    [
      packages.certifi
      packages.chardet
      packages.docopt
      packages.jinja2
      packages.pip
      packages.pycodestyle
      packages.setuptools
      packages.unidecode
      nixPython.jinja2-ansible-filters
    ]
  );
  texlive = nixpkgs.texlive;
  texliveEnvironment = texlive.combine {
    inherit (texlive) scheme-infraonly dvipng;
  };
  nixNodeJs = import distributions.nixNodeJsPath { pkgs = nixpkgs; };
  nodeJsPackages = [
    nixNodeJs."css-validator-0.9.0"
    nixNodeJs."sass-1.26.7"
  ];
in {
  inherit (nixpkgs) buildEnv mkShell;
  inherit (python.pkgs) buildPythonPackage;
  packages = [ pythonEnvironment texliveEnvironment ]
             ++ nodeJsPackages;
}
  b
### End of file
