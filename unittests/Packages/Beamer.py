import pytest
from plasTeX.TeX import TeX

@pytest.mark.xfail
def test_beamer_args():
    tex = TeX()
    tex.input(r'''
\documentclass{beamer}
\renewcommand<>{\highlight}[2][structure]{{\textcolor#3{#1}{#2}}}
\begin{document}
\highlight{text}
\end{document}''')

    p = tex.parse()

    # SImply test that parsing caused no error
    assert True
