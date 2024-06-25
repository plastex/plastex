from plasTeX.TeX import TeX

def test_bbm():
    t = TeX()
    t.input(r'''
\documentclass{article}
\usepackage{bbm}
\begin{document}
    $ \mathbbm{1} $
\end{document}
''')
    p = t.parse()
    assert p.getElementsByTagName('math')[0].source == r'$ \mathbb{1} $'
