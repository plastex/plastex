# Contributing to plasTeX

## A bit of history

plasTeX is a *very* old Python project. The first public release was in 2001,
under the name pyLaTeX. But the code base started before that, using Python
1.5, probably around 1999. This was two years before PEP8 was written and
*long* before many features of modern python were introduced in the language. 
Although it now runs on present day versions of Python, the code style is very
far from modern in most places. Modernizing it would be a huge undertaking and
nobody ever talked about having time for it. Contributions are welcome (but see
the warning about tests below).

Kevin Smith is the author of most of the plasTeX codebase. He later received
help from Tim Arnold. In 2019, maintaince was transferred to Patrick Massot who
wrote the HTML5 renderer around 2016 but has very little time for this project
(but still a tiny bit more time than Kevin or Tim).

Because the code base is so old and the current maintainer wrote almost nothing
of it, it is even more crucial than usual that every proposed modification comes with
unit tests clearly showing what was failing and how it is fixed.

## Testing

We run our tests using [pytest](https://docs.pytest.org/en/latest/),
although many of our tests were written long before pytest was written. 
As usual with pytest, not much will work as expected if you don't install
the package you want to test. So the first step is to run 
`pip install .` in the toplevel folder of this repository, the one
containing `setup.py` (as usual, depending on your Python setup, `pip`
could be called `pip3`, and you may need administration permissions if
you want to make a system-wide install). 
If you want to quickly modify code and retest, it is more convenient to
use "editable install", by running `pip install -e .` which creates a
link to your working copy of plasTeX instead of copying it (see 
[pip's documentation](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs)
if needed).
Once plasTeX is installed, you can run `pytest` from the toplevel
folder.

Our continuous integration tests plasTeX using Python 3.6 to 3.12. 
This can be done locally using
[tox](https://tox.readthedocs.io/en/latest/). For this you need `tox`
of course, but also various versions of python. One convenient way
to ensure that is to use [pyenv](https://github.com/pyenv/pyenv).
After setting up `pyenv` and installing, say Python 3.6.8,
3.7.2, 3.8.0, 3.9.0, 3.10.0, 3.11.0, 3.12.1 (using `pyenv install 3.5.6` etc.), you can
create, inside the toplevel folder of your working copy of plasTeX, a file
`.python-version` containing
```
3.12.1
3.11.0
3.10.0
3.9.0
3.8.0
3.7.2
3.6.8
```
Then you can run `tox` to run our test suite against all those versions
of Python.
