from pathlib import Path

from plasTeX.TeX import TeX
from plasTeX.Renderers.HTML5 import Renderer

def test_intro_snippet(tmpdir):
    (Path(tmpdir)/'test.tex').write_text(r"""
    \documentclass{article}
    \begin{document}
    Hello.
    \end{document}
    """)
    with tmpdir.as_cwd():
        Renderer().render(TeX(file='test.tex').parse())
    assert (Path(tmpdir)/'index.html').exists()
    assert 'Hello' in (Path(tmpdir)/'index.html').read_text()
