packages:

let
  nixpkgs = import <nixpkgs> {};
  jinja2-ansible-filters =
    nixpkgs.callPackage ./jinja2-ansible-filters.nix packages;
in packages.buildPythonPackage {
  name = "plastex";
  src = ./..;
  doCheck = false;
  propagatedBuildInputs = [
    packages.certifi
    packages.chardet
    packages.docopt
    packages.jinja2
    packages.pip
    packages.pycodestyle
    packages.setuptools
    packages.unidecode

    jinja2-ansible-filters
  ];
}
