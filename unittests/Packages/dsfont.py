from plasTeX.TeX import TeX

def test_dsfont():
    t = TeX()
    t.input(r'''
\documentclass{article}
\usepackage{dsfont}
\begin{document}
$ \mathds{x} $
\end{document}
''')
    p = t.parse()

    assert p.getElementsByTagName('math')[0].source == r'$ \mathbb{x} $'
