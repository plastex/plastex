with import <nixpkgs> {};

let
  python = python38;
  jinja2-ansible-filters =
    callPackage nix/jinja2-ansible-filters.nix python.pkgs; 
in python.withPackages (packages: [
  packages.certifi
  packages.chardet
  packages.docopt
  packages.jinja2
  packages.pip
  packages.pycodestyle
  packages.setuptools
  packages.unidecode

  jinja2-ansible-filters
])
