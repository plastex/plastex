import pytest
from plasTeX.TeX import TeX

def test_amsbsy():
    tex = TeX()
    tex.input(r'''
\documentclass{article}
\usepackage{amsbsy}
\begin{document}
$\boldsymbol{\infty}$
\end{document}''')

    doc = tex.parse()

    # SImply test that parsing caused no error
    assert len(doc.getElementsByTagName('boldsymbol')) == 1
