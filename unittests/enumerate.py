import pytest
from plasTeX.TeX import TeX

def test_enumerate():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      \begin{enumerate}
        \item First
        \item Second
      \end{enumerate}

      \begin{enumerate}[a)]
        \item First
        \item Second
      \end{enumerate}

      \begin{enumerate}[<I>]
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
        \item a
      \end{enumerate}
      \end{document}
      ''')
    enums = tex.parse().getElementsByTagName('enumerate')
    items = enums[0].getElementsByTagName('item')
    assert len(items) == 2
    assert items[0].position == 1
    assert enums[0].term(items[0].position) == '1.'
    assert enums[0].term(items[1].position) == '2.'

    items = enums[1].getElementsByTagName('item')
    assert enums[1].term(items[0].position) == 'a)'
    assert enums[1].term(items[1].position) == 'b)'

    items = enums[2].getElementsByTagName('item')
    assert enums[2].term(items[0].position) == '<I>'
    assert enums[2].term(items[11].position) == '<XII>'
