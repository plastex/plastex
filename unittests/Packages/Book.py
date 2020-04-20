from plasTeX.TeX import TeX

def test_book_toc():
    t = TeX()
    t.input(r'''
\documentclass{book}
\begin{document}
\chapter{A}
\part{B}
\chapter{C}
\end{document}
''')
    p = t.parse()
    print(p.getElementsByTagName("chapter"))
    assert ['1', '2'] == [x.ref.source for x in p.getElementsByTagName("chapter")]
