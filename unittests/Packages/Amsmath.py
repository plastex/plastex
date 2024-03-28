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
    equations = output.getElementsByTagName('equation')
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

DOC_subequations = r"""
\documentclass{article}

\usepackage{amsmath}

\begin{document}

Subequations

\begin{subequations}\label{s1}
\begin{equation}
x = 1 \label{e1a}
\end{equation}
\begin{equation}
y = 2\label{e1b}
\end{equation}
\end{subequations}

Equation with no tag

\begin{equation}\label{e2}
c = c
\end{equation}

Equation with tag

\begin{equation}\label{ez}
 a = f \tag{z}
\end{equation}

Subequations again

\begin{subequations}\label{s2}
    \begin{equation}
    x = 1\label{e2a}
    \end{equation}
    \begin{equation}
    y = 2\tag{y}\label{e2y}
    \end{equation}
    \begin{equation}
    y = 3\label{e2b}
    \end{equation}
\end{subequations}

Refs: \ref{s1} \ref{e1a} \ref{e1b} \ref{e2} \ref{ez} \ref{s2} \ref{e2a} \ref{e2y} \ref{e2b}

\end{document}
"""

def test_subequations():
    s = TeX()
    s.input(DOC_subequations)
    output = s.parse()

    equations = output.getElementsByTagName('equation')
    print(equations)

    equation_refs = [
        '1a',
        '1b',
        '2',
        'z',
        '3a',
        'y',
        '3b',
    ]

    for i, ref in enumerate(equation_refs):
        assert equations[i].ref.textContent == ref

    subequations = output.getElementsByTagName('subequations')

    subequations_refs = [
        '1',
        '3',
    ]

    for i, ref in enumerate(subequations_refs):
        assert subequations[i].ref.textContent == ref
