### Project development dependencies

let
  distributions = import ./distributions.nix;
  python = distributions.python;
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
      distributions.nixPython.jinja2-ansible-filters
    ]
  );
  nixpkgs = distributions.nixpkgs;
  texlive = nixpkgs.texlive;
  texLiveEnvironment = texlive.combine {
    inherit (texlive) scheme-infraonly dvipng;
  };
  nodeJsPackages = with distributions; [
    nixNodeJs."css-validator-0.9.0"
    nixNodeJs."sass-1.26.7"
  ];
in {
  inherit (nixpkgs) buildEnv mkShell;
  inherit (python.pkgs) buildPythonPackage;
  packages = [ pythonEnvironment texLiveEnvironment ]
             ++ nodeJsPackages;
}

### End of file
