import pytest
from plasTeX.TeX import TeX

def test_ensuremath():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \newcommand{\dx}{\ensuremath{dx}}
      \begin{document}
      In $\int f(x)\, \dx$, the \dx{} is an infinitesimal.
      \end{document}
      ''')
    nodes = tex.parse().getElementsByTagName('math')
    assert len(nodes) == 1
    assert nodes[0].mathjax_source == r'\(\int f(x)\,  dx\)'
    nodes = tex.parse().getElementsByTagName('ensuremath')
    assert len(nodes) == 2
    assert nodes[1].mathjax_source == r'dx'


def test_ensuremath_more():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      $\ensuremath{\alpha}$
      \ensuremath{\delta}
      $\ensuremath{\beta} + \gamma$
      \end{document}
      ''')
    math = tex.parse().getElementsByTagName('math')
    assert math[0].mathjax_source == r'\(\alpha \)'
    assert math[1].mathjax_source == r'\(\beta  + \gamma \)'
    emath = tex.parse().getElementsByTagName('ensuremath')
    assert emath[1].mathjax_source == r'\delta '
