from plasTeX.TeX import TeX

def test_amscd():
    t = TeX()
    t.input(r'''
\documentclass{article}
\usepackage{amscd}
\begin{document}
    \begin{equation} \begin{CD}
        A @>>> B @>>> C \\
        @VVV @AAA D @VVV \\
        E @<<< F @<<\alpha< G
    \end{CD} \end{equation}
\end{document}
''')
    p = t.parse()
    assert p.getElementsByTagName('equation')[0].source == r'''\begin{equation}  \begin{CD} 
        A @>>> B @>>> C \\
        @VVV @AAA D @VVV \\
        E @<<< F @<<\alpha< G
    \end{CD} \end{equation}'''

