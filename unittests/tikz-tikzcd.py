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

from bs4 import BeautifulSoup

config = config + html5_config

def test_tikz(tmpdir):
    try:
        tmpdir = Path(tmpdir)
    except TypeError: # Fallback for older python
        tmpdir = Path(str(tmpdir))

    root = Path(__file__).parent
    test_id = "tikz-pdf2svg-gspdfpng"

    benchdir = root / "benchmarks" / test_id
    newdir = root / "new" / test_id

    img_files = ["images/img-0001.svg", "images/img-0002.svg", "images/img-0001.png", "images/img-0002.png"]

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

    def new_file(base: str):
        newfile = newdir / base
        newfile.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(str(tmpdir / base), str(newfile))

    # Compare html output
    changed = False
    htmlError = False

    try:
        with open(str(tmpdir / "index.html")) as fd:
            new_soup = BeautifulSoup(fd, "html.parser")

        with open(str(benchdir / "index.html")) as fd:
            bench_soup = BeautifulSoup(fd, "html.parser")

        def cmp(tag: str):
            new = list(new_soup.find_all("div", tag))
            bench = list(bench_soup.find_all("div", tag))
            if len(bench) != 1:
                htmlError = True
                print("More than one <div class='{}'> node found in benchmark".format(tag), file=sys.stderr)

            if len(new) != 1:
                htmlError = True
                print("More than one <div class='{}'> node found in output".format(tag), file=sys.stderr)

            if new[0] != bench[0]:
                htmlError = True
                print("Differences were found in the <div class='{}'> node".format(tag), file=sys.stderr)
                print("Benchmark: {}".format(bench[0]), file=sys.stderr)
                print("New: {}".format(new[0]), file=sys.stderr)

        cmp("tikzpicture")
        cmp("tikzcd")

        if htmlError:
            new_file("index.html")

    except OSError as e:
        htmlError = True
        if e.filename == str(tmpdir / "index.html"):
            print('Missing output file: index.html', file=sys.stderr)
        else:
            print('Missing benchmark file: index.html', file=sys.stderr)
            new_file("index.html")

    # Compare image output
    match, mismatch, errors = filecmp.cmpfiles(str(tmpdir), str(benchdir), img_files, shallow=False)

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

    if htmlError or (len(errors) + len(mismatch) > 0):
        assert False
