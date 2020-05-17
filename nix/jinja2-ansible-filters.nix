packages:

packages.buildPythonPackage rec {
  pname = "jinja2-ansible-filters";
  version = "1.3.0";

  src = packages.fetchPypi {
    inherit pname version;
    sha256 = "7a4e6f86ffa814841e72d0c3c22c7e727bcb8387d7b85e4224a1181634a361b4";
  };

  prePatch = ''
    substituteInPlace setup.cfg --replace \
      "version = file: VERSION" "version = ${version}"
  '';

  propagatedBuildInputs = [ packages.jinja2 packages.pyyaml ];
}
