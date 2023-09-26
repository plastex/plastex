from plasTeX.TeX import TeX

def test_href_no_char_sub():
    """Test for issue #342"""
    tex = TeX()
    tex.input(r'''
\documentclass{article}
\usepackage{hyperref}
\begin{document}
    \href{a--file.pdf}{View file --}.

    A bit of text -- like that.
\end{document}
''')

    hrefs = tex.parse().getElementsByTagName('href')

    assert len(hrefs) == 1
    assert hrefs[0].attributes['url'].textContent == 'a--file.pdf'

