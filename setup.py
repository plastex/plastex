#!/usr/bin/env python

from distutils.core import setup

setup(name="plasTeX",
      description="LaTeX document parser and converter",
      author="Kevin Smith",
      author_email="Kevin.Smith@theMorgue.org",
      #url="",
      packages=['plasTeX','plasTeX.ConfigManager','plasTeX.DOM',
                'plasTeX.imagers','plasTeX.packages','plasTeX.renderers',
                'plasTeX.renderers.xhtml','plasTeX.simpletal',
                'plasTeX.Base','plasTeX.Base.LaTeX','plasTeX.Base.TeX'],
      scripts=['plasTeX/plastex'],
)

