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

from plasTeX.Config import config as base_config
from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX, TeXDocument

def test_tikz(tmpdir):
    try:
        tmpdir = Path(tmpdir)
    except TypeError: # Fallback for older python
        tmpdir = Path(str(tmpdir))

    root = Path(__file__).parent
    test_id = "tikz-pdf2svg-gspdfpng"

    benchdir = root / "benchmarks" / test_id
    newdir = root / "new" / test_id

    files = ["images/img-0001.svg", "images/img-0002.svg", "images/img-0001.png", "images/img-0002.png", "index"]

    config = base_config.copy()
    config['images']['vector-imager'] = 'pdf2svg'
    config['images']['imager'] = 'gspdfpng'

    doc = TeXDocument(config=config)
    tex = TeX(doc)

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

    def render_image(obj):
        return "{}\n{}\n".format(obj.vectorImage.url, obj.image.url)

    renderer["tikzpicture"] = render_image
    renderer["tikzcd"] = render_image

    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    os.chdir(cwd)

    def new_file(base: str):
        newfile = newdir / base
        newfile.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(tmpdir / base), str(newfile))

    # Compare image output
    match, mismatch, errors = filecmp.cmpfiles(str(tmpdir), str(benchdir), files, shallow=False)

    for f in mismatch:
        print('Differences were found: %s' % f, file=sys.stderr)
        new_file(f)

    for f in errors:
        if not (tmpdir / f).exists():
            print('Missing output file: %s' % f, file=sys.stderr)
        elif not (benchdir / f).exists():
            print('Missing benchmark file: %s' % f, file=sys.stderr)
            new_file(f)
        else:
            print('Failed to compare: %s' % f, file=sys.stderr)

    if len(errors) + len(mismatch) > 0:
        assert False
