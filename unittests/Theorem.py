from plasTeX.TeX import TeX
from plasTeX.Base.TeX.Primitives import par

def test_single_paragraph_theorem():
    """Check single paragraph theorem does contain a paragraph"""
    tex = TeX()
    tex.input(r'''
      \newtheorem{thm}{Theorem}
      \begin{thm}
      a b c
      \end{thm}
      ''')
    nodes = tex.parse().getElementsByTagName('thm')[0].childNodes
    assert len(nodes) == 1
    assert isinstance(nodes[0], par)
