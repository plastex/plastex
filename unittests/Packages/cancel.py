from plasTeX.TeX import TeX

def test_cancel():
    t = TeX()
    t.input(r'''
\documentclass{article}
\usepackage{cancel}
\begin{document}
\( \cancel{x} \xcancel{x} \bcancel{x} \cancelto{y}{x} \)
\end{document}
''')
    p = t.parse()
    assert p.getElementsByTagName('math')[0].source == r'$ \cancel{x} \xcancel{x} \bcancel{x} \cancelto{y}{x} $'
