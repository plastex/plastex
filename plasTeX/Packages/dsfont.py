"""
The LaTeX package doublestroke (imported as dsfont) supplies a font of double-struck characters.

This implements the package in plasTeX by rewriting \mathds{.} to \mathbb{.}, so MathJax will use doublestruck characters from its fonts.

MathJax v4 will add proper support for dsfont: https://github.com/mathjax/MathJax-src/pull/1057
"""

from plasTeX import Command, sourceArguments


class mathds(Command):
    args = 'self'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
