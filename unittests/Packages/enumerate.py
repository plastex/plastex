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

      \begin{enumerate}
        ignore this
        \item First
        \vspace{1em} % also ignored
        \item Second
      \end{enumerate}

      \end{document}
      ''')

    enums = tex.parse().getElementsByTagName('enumerate')

    items = enums[0].getElementsByTagName('item')
    assert len(items) == 2

    items = enums[1].getElementsByTagName('item')
    assert len(items) == 2
