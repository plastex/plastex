from plasTeX.TeX import TeX

DOC_numberwithin = r"""
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
    s.input(DOC_numberwithin)
    output = s.parse()
    equations =output.getElementsByTagName('equation')
    assert equations[0].ref.textContent == '1.1'
    assert equations[1].ref.textContent == '2.1'
    assert equations[2].ref.textContent == '2.2'

DOC_imath = r"""
\documentclass{article}

\begin{document}

$\imath$ $\jmath$

\end{document}
"""

def test_imath():
    s = TeX()
    s.input(DOC_imath)
    output = s.parse()

    imath = output.getElementsByTagName('imath')[0]
    assert len(imath.childNodes) == 0
    assert imath.str == chr(305)
    jmath = output.getElementsByTagName('jmath')[0]

    assert len(jmath.childNodes) == 0
    assert jmath.str == chr(567)

DOC_split = r"""
\documentclass{article}

\usepackage{amsmath}

\begin{document}

\begin{equation}
\begin{split}
 a\\ b\\ c\\d
\end{split}
\end{equation}

\begin{equation}
a
\end{equation}

\end{document}
"""

def test_split():
    """ 
        The split environment provides no numbering.
    """
    s = TeX()
    s.input(DOC_split)
    output = s.parse()
    equations = output.getElementsByTagName('equation')

    assert equations[0].ref.textContent == '1'
    assert equations[1].ref.textContent == '2'
