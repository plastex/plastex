### Install the project in development mode

{
  stdenv, buildPythonPackage, cleanSource, certifi, chardet, docopt,
  jinja2, unidecode, jinja2-ansible-filters, dvipng
}:

buildPythonPackage {
  name = "plastex";
  src = cleanSource ./..;
  doCheck = false;
  propagatedBuildInputs = [
    certifi chardet docopt jinja2 unidecode jinja2-ansible-filters
    dvipng
  ];
  meta = {
    description = "Convert LaTeX documents to various formats";
    homepage = "https://github.com/nyraghu/plastex";
    license = [ stdenv.lib.licenses.mit ];
    maintainers = [
      {
        email = "raghu@hri.res.in";
        github = "nyraghu";
        githubId = 11349287;
        name = "N. Raghavendra";
      }
    ];
  };
}

### End of file
