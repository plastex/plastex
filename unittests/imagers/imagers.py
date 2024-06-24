"""
This file runs imager tests by compiling TeX files and comparing
with reference output images.
The "benchmarks" folder containing the expected outputs.

Each time such a test fails, the output is placed into a "new" folder.
This allows both easy comparison and replacement of the benchmark in
case the change is desired.
"""

import os, shutil, difflib
from pathlib import Path
import pytest

from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX

# Add the unittests directory to the sys path so that the helpers module
# can be imported when this test is run on its own.
import sys
sys.path.append(str(Path(__file__).parent.parent))

from helpers.utils import cmp_img

@pytest.mark.parametrize('imager_tuple',
        [('dvipng', '.png', None),
         ('dvisvgm', '.svg', None),
         ('gsdvipng', '.png', None),
         ('gspdfpng', '.png', None),
         ('pdf2svg', '.svg', None),
         ('pdf2svg', '.svg', 'xelatex'),
         ('pdf2svg', '.svg', 'lualatex'),
         ('pdftoppm', '.png', None)],
        ids=lambda p: p[0] + "-" + str(p[2]))
def test_imager(imager_tuple, tmpdir):
    imager, ext, compiler = imager_tuple
    if ext == ".svg":
        kind = "vector-imager"
    else:
        kind = "imager"

    tmpdir = Path(str(tmpdir)) # for old pythons

    tex = TeX()
    tex.ownerDocument.config['images'][kind] = imager
    if compiler is not None:
        tex.ownerDocument.config['images'][kind.replace("imager", "compiler")] = compiler

    tex.input(r'''
    \documentclass{article}
    \AtBeginDocument{You should not be seeing this in the imager output. This
    is injected into the document with \textbackslash AtBeginDocument. The actual
    image is on the second page and the imager should get the images from
    there.}
    \begin{document}
    $a + b = x$
    \end{document}
    ''')

    renderer = Renderer()
    if kind == "imager":
        renderer['math'] = lambda node: node.image.url
    else:
        renderer['math'] = lambda node: node.vectorImage.url

    directory = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    os.chdir(directory)

    outfile = tmpdir/'images'/('img-0001' + ext)
    root = Path(__file__).parent

    benchfile = root/'benchmarks'/"{}-{}{}".format(imager, compiler, ext)
    if not benchfile.exists():
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/benchfile.name))
        raise OSError('No benchmark file: %s' % benchfile)

    diff = cmp_img(str(benchfile.absolute()), str(outfile.absolute()))

    if (ext == '.svg' and diff > 0.0001) or diff > 0.01:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/benchfile.name))

        if ext == '.svg':
            bench = benchfile.read_text().split('\n')
            output = outfile.read_text()
            print('SVG differences:\n','\n'.join(difflib.unified_diff(
                bench, output.split('\n'), fromfile='benchmark', tofile='output')).strip())
            print('Full svg:\n\n', output)
        assert False, 'Differences were found:\n' + str(diff)
