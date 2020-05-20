import pytest

from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX
from plasTeX.Imagers import Imager

class NullImager(Imager):
    def getImage(self, node):
        raise ValueError

@pytest.mark.parametrize('enable_bitmap', [True, False])
def test_imager(enable_bitmap, tmpdir):
    with tmpdir.as_cwd():
        tex = TeX()
        tex.ownerDocument.config['images']["imager"] = "none"
        tex.ownerDocument.config['images']["vector-imager"] = "pdf2svg"

        tex.input(r'''
        \documentclass{article}
        \begin{document}
        $a + b = x$
        \end{document}
        ''')

        doc = tex.parse()
        renderer = Renderer()
        renderer.imager = NullImager(doc)
        renderer.vectorBitmap = enable_bitmap
        renderer['math'] = lambda node: node.vectorImage.url

        if enable_bitmap:
            with pytest.raises(ValueError):
                renderer.render(doc)
        else:
            renderer.render(doc)
