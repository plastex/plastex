from plasTeX.TeX import TeX

def test_proof_in_par():
    """Check proof environment ends the current paragraph."""
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}

      a
      \begin{proof}
      b
      \end{proof}
      c

      \end{document}
      ''')
    doc = tex.parse()
    proof = doc.getElementsByTagName('proof')[0]
    if len(proof.parentNode.childNodes) != 1:
        print(doc.toXML())
        assert False

def test_proof_block_type():
    """
    Check proof environment ends up inside a blockType paragraph. This in
    particular makes HTML5 not wrap the resulting object in <p></p> tags.
    """
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}

      a

      \begin{proof}
      b
      \end{proof}

      c

      \end{document}
      ''')
    doc = tex.parse()
    proof = doc.getElementsByTagName('proof')[0]
    if not proof.parentNode.blockType:
        print(doc.toXML())
        assert False
