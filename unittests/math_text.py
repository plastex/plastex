from plasTeX.TeX import TeX

def test_textrm():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      $\textrm{plastex}$
      \end{document}
      ''')
    nodes = tex.parse().getElementsByTagName('math')
    assert len(nodes) == 1
    assert nodes[0].textContent == 'plastex'

def test_math_in_textrm():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      $\textrm{$x$}$
      \end{document}
      ''')
    assert tex.parse().getElementsByTagName('math')[0].textContent == 'x'
