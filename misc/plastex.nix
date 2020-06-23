{
  pythonPackages,
  jinja2-ansible-filters
}:

pythonPackages.buildPythonPackage {
  name = "plastex";
  src = ./..;
  doCheck = false;
  propagatedBuildInputs = [
    pythonPackages.certifi
    pythonPackages.chardet
    pythonPackages.docopt
    pythonPackages.jinja2
    pythonPackages.pip
    pythonPackages.pycodestyle
    pythonPackages.setuptools
    pythonPackages.unidecode
    jinja2-ansible-filters
  ];
}
