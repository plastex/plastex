# plastex

Read more at the github page for the plasTeX project:  http://tiarno.github.io/plastex/

Installation of this package is done just like any other Python package.
See the INSTALL file for details.

Once you have plasTeX installed, you can use the command-line utility,
called "plastex" just like latex or pdflatex.  For example, if you
have a LaTeX file called mybook.tex, simple run:

```
plastex mybook.tex
```

This will convert mybook.tex into XHTML (the default renderer).  Of course,
there are many options to control the execution of plastex.  Simply type
"plastex" on the command line without options or arguments to see the
full list of command-line options.

It is also possible to write your own command-line utilities that leverage
the power of the plasTeX framework.  In fact, the essence of the "plastex"
command can be written in just one line of code (not including the Python
import commands):

```
import sys
from plasTeX.TeX import TeX
from plasTeX.Renderers.XHTML import Renderer
Renderer().render(TeX(file=sys.argv[1]).parse())
```

plasTeX is really much more than just a LaTeX-to-other-format converter 
though.  See the documentation at http://tiarno.github.io/plastex/ for a complete
view of what it is capable of.

## Testing
To run the tests locally, make sure you have a [virtual env](https://docs.python.org/3/library/venv.html) enabled, and all the requirements installed, then run pytest:
```
# install venv and requirements (optional, recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# run the tests
pytest
```

## Status
[![Build Status](https://travis-ci.org/niklasp/plastex.svg?branch=python3)](https://travis-ci.org/niklasp/plastex)
[![Coverage Status](https://coveralls.io/repos/github/niklasp/plastex/badge.svg?branch=python3)](https://coveralls.io/github/niklasp/plastex?branch=python3)

