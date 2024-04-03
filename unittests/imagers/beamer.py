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

import sys
sys.path.append(str(Path(__file__).parent.parent))

from helpers.utils import cmp_img

def test_beamer_svg(tmpdir):
    imager = 'pdf2svg'
    ext = '.svg'
    compiler = None
    kind = "vector-imager"

    tmpdir = Path(str(tmpdir)) # for old pythons

    tex = TeX()
    tex.ownerDocument.config['images'][kind] = imager

    tex.input(r'''
    \documentclass{beamer}
    \setbeamercolor{background canvas}{bg=violet}
    \begin{document}
    \begin{frame}
        $a + b = x$
    \end{frame}
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

    benchfile = root/'benchmarks'/'beamer.svg'
    if not benchfile.exists():
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/benchfile.name))
        raise OSError('No benchmark file: %s' % benchfile)

    diff = cmp_img(str(benchfile.absolute()), str(outfile.absolute()))

    if (ext == '.svg' and diff > 0.0001) or diff > 0.01:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/benchfile.name))

        bench = benchfile.read_text().split('\n')
        output = outfile.read_text()
        print('SVG differences:\n','\n'.join(difflib.unified_diff(
            bench, output.split('\n'), fromfile='benchmark', tofile='output')).strip())
        print('Full svg:\n\n', output)
        assert False, 'Differences were found:\n' + str(diff)
