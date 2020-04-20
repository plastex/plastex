
from plasTeX.TeX import TeX

def test_counter():
    t = TeX()
    t.input(r'''
\documentclass{book}
\begin{document}
\begin{figure}\caption{A}\end{figure}
\section{B}
\chapter{C}
\section{D}
\begin{figure}\caption{E}\end{figure}
\end{document}
    ''')

    p = t.parse()

    assert [x.ref.source for x in p.getElementsByTagName("caption")] == ["1", "1.1"]
    assert [x.ref.source for x in p.getElementsByTagName("section")] == ["0.1", "1.1"]
