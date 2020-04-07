"""
This file runs imager tests by compiling TeX files and comparing
with reference output images.
The "benchmarks" folder containing the expected outputs.

Each time such a test fails, the output is placed into a "new" folder.
This allows both easy comparison and replacement of the benchmark in
case the change is desired.
"""

import filecmp
import os, shutil
import sys
from pathlib import Path

from plasTeX.Config import config
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Renderers.HTML5.Config import config as html5_config
from plasTeX.TeX import TeX, TeXDocument

config = config + html5_config

def test_imager(tmpdir):
    tmpdir = Path(tmpdir) # for old pythons
    root = Path(__file__).parent
    test_id = "tikz-pdf2svg-gspdfpng"

    benchdir = root / "benchmarks" / test_id
    newdir = root / "new" / test_id

    files = ["images/img-0001.svg", "images/img-0002.svg", "images/img-0001.png", "images/img-0002.png", "index.html"]

    doc = TeXDocument(config.copy())
    tex = TeX(doc)
    tex.ownerDocument.config['images']['vector-imager'] = 'pdf2svg'
    tex.ownerDocument.config['images']['imager'] = 'gspdfpng'

    tex.input(r'''
    \documentclass{article}
    \usepackage{tikz}
    \usepackage{tikz-cd}
    \begin{document}
    \begin{tikzpicture}
        \draw (0, 0) -- (0, 2) -- (2, 0) -- (0, 0);
    \end{tikzpicture}

    \begin{tikzcd}
        A \ar[r, "i"] & B \ar[d, "p"] \\ & C
    \end{tikzcd}
    \end{document}
    ''')

    renderer = Renderer()

    directory = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    os.chdir(directory)

    match, mismatch, errors = filecmp.cmpfiles(tmpdir, benchdir, files, shallow=False)

    def new_file(base):
        newfile = newdir / base
        newfile.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(tmpdir / base), str(newfile))

    for f in mismatch:
        print('Differences were found: %s' % f, file=sys.stderr)
        new_file(f)

    for f in errors:
        if not (benchdir / f).exists():
            print('Missing benchmark file: %s' % f, file=sys.stderr)
            new_file(f)
        elif not (tmpdir / f).exists():
            print('Missing output file: %s' % f, file=sys.stderr)
        else:
            print('Failed to compare: %s' % f, file=sys.stderr)

    if len(errors) + len(mismatch) > 0:
        assert False
