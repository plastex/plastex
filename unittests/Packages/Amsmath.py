from plasTeX.TeX import TeX

DOC = r"""
\documentclass{article}
\usepackage{amsmath}
\numberwithin{equation}{section}
\begin{document}
\section{First section}
\begin{equation}
a = b
\end{equation}
\section{Second section}
\begin{equation}
c = d
\end{equation}
\subsection{Subsection}
\begin{equation}
e = f
\end{equation}
\end{document}
"""

def test_numberwithin():
    s = TeX()
    s.input(DOC)
    output = s.parse()
    equations =output.getElementsByTagName('equation')
    assert equations[0].ref.textContent == '1.1'
    assert equations[1].ref.textContent == '2.1'
    assert equations[2].ref.textContent == '2.2'
