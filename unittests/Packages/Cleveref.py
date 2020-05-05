from plasTeX.TeX import TeX

def test_cleveref():
    tex = TeX()
    tex.input(r'''
\documentclass{article}
\usepackage{cleveref}
\newtheorem{thm}{TheoRem}
\begin{document}
\section{Foo}\label{sec}
\begin{figure}
  \caption{Test}
  \label{fig}
\end{figure}
\subsection{Bar}\label{subsec}
\begin{thm}
  \label{thm}
\end{thm}
\begin{equation}
  x = y\label{eq}
\end{equation}
\Cref{sec}\Cref{fig}\Cref{subsec}\Cref{thm}\Cref{eq}
\cref{sec}\cref{fig}\cref{subsec}\cref{thm}\cref{eq}
\end{document}
''')

    p = tex.parse()

    assert ["Section", "Figure", "Section", "TheoRem", "Equation"] == [x.refname() for x in p.getElementsByTagName("Cref")]
    assert ["section", "figure", "section", "theoRem", "eq."] == [x.refname() for x in p.getElementsByTagName("cref")]
