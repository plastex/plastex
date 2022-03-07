from plasTeX.TeX import TeX

def test_comparison_operator():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      $0 < 1$ and $2 > 1$.
      \end{document}
      ''')
    nodes = tex.parse().getElementsByTagName('math')
    assert len(nodes) == 2
    assert nodes[0].mathjax_source == r'\(0 {\lt} 1\)'
    assert nodes[1].mathjax_source == r'\(2 {\gt} 1\)'

def test_angle_brackets():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      $\left<u, v\right>$
      \end{document}
      ''')
    math = tex.parse().getElementsByTagName('math')[0]
    assert math.mathjax_source == r'\(\left\langle u, v\right\rangle \)'
