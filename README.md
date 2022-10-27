# plastex

plasTeX is a LaTeX compiler written in Python.
Read more at the github page for the plasTeX project:
http://plastex.github.io/plastex/

## Installation
plasTeX can be installed like any usual Python package.

For instance, you can install it using [pip](https://pip.pypa.io/en/stable/) by typing
`pip install plastex`
at a shell prompt. This will install the latest version of plasTeX packaged [on PyPi](https://pypi.org/project/plasTeX/).
As of October 2022, the last version is almost three years old: you may want to install the latest version from github. For this,
- clone the repository, e.g. `git clone https://github.com/plastex/plastex`
- install the latest version of plasTeX: `pip install ./plastex`
(Mercurial users using [`hg-git`](https://hg-git.github.io/) can run `hg clone https://github.com/plastex/plastex` in the first step instead.)

Updating an existing version of plastex can be done by updating the github repository, then running `pip install --upgrade plastex`.

## Using plastex
plasTeX can do many things:
- it can simply compile your LaTeX document into nice-looking HTML,
- there are many options to configure the output,
- plasTeX can also be used as a library from other Python programs,
- finally, plasTeX can be extended in many ways!

If you just want to compile your document, type `plastex myfile.tex` into a shell and you're good.
If you're interested in the other options, take a look at the [user guide](https://plastex.github.io/plastex/plastex/index.html).
If you want to extend plasTeX to match your needs, the [tutorial](https://plastex.github.io/plastex/tutorials/) could be a useful starting point. Or take a look at the different users of plastex](https://plastex.github.io/plastex/#users).

## Contributing
- Do you welcome contributions in general?
- Anything particular to watch out for?
- Are there any "good first issues"? How could one help? Are there any tasks that just need to be done, which one could do?
If there's something to say on either of they, this could be a place to mention them.

And even if it's just:
"If you see a bug fix or an improvement to the documentation, feel free to just send a pull request.
This project is maintained as a hobby project. We welcome contributions, but it might take a week before we reply."

## Testing
To run the tests locally, run `tox`.
This will run tests locally using Python 3.6 to 3.10.

## Status
[![Build Status](https://github.com/plastex/plastex/workflows/tests/badge.svg)](https://github.com/plastex/plastex/actions)
[![Coverage Status](https://coveralls.io/repos/github/plastex/plastex/badge.svg?branch=master)](https://coveralls.io/github/plastex/plastex?branch=master)

