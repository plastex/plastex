from plasTeX.TeX import TeX

def test_slash():
    tex = TeX()
    tex.input(r'''
        \documentclass{article}
        \begin{document}A \slash B\end{document}
    ''')

    output = tex.parse()

    assert output.getElementsByTagName('document')[0].textContent == 'A /B'
