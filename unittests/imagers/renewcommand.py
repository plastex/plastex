import os
from pathlib import Path

from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX

def test_renewcommand_with_imager(tmpdir):
    imager, ext, compiler = ('pdf2svg', '.svg', None)
    kind = "vector-imager"

    tmpdir = Path(str(tmpdir)) # for old pythons

    tex = TeX()
    tex.ownerDocument.config['images'][kind] = imager
    if compiler is not None:
        tex.ownerDocument.config['images'][kind.replace("imager", "compiler")] = compiler

    tex.input(r'''
    \documentclass{article}
    \renewcommand{\>}{\rangle}
    \begin{document}
    $a + b = x$
    $\>$
    \end{document}
    ''')

    renderer = Renderer()
    renderer['math'] = lambda node: node.vectorImage.url

    directory = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    os.chdir(directory)

    outfile = tmpdir/'images'/('img-0001' + ext)
    root = Path(__file__).parent

    assert outfile.exists(), "No image was created."

