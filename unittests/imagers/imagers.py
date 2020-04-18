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

from helpers.utils import cmp_img

@pytest.mark.parametrize('imager_tuple',
        [('pdf2svg', '.svg', 'vector-imager', 'pdflatex'),
         ('pdf2svg', '.svg', 'vector-imager', 'xelatex'),
         ('pdf2svg', '.svg', 'vector-imager', 'lualatex'),
         ('dvisvgm', '.svg', 'vector-imager', 'latex'),
         ('dvipng', '.png', 'imager', 'latex')],
        ids=lambda p: p[0])
def test_imager(imager_tuple, tmpdir):
    imager, ext, kind, compiler = imager_tuple
    tmpdir = Path(str(tmpdir)) # for old pythons

    tex = TeX()
    tex.ownerDocument.config['images'][kind] = imager
    tex.ownerDocument.config['images']["compiler"] = compiler
    tex.input(r'''
    \documentclass{article}
    \begin{document}
    $a + b = x$
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
