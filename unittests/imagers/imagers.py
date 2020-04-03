"""
This file runs imager tests by compiling TeX files and comparing
with reference output images. 
The "benchmarks" folder containing the expected outputs. 

Each time such a test fails, the output is placed into a "new" folder.
This allows both easy comparison and replacement of the benchmark in
case the change is desired.
"""

import os, shutil
from pathlib import Path
import pytest

from plasTeX.Renderers import Renderer
from plasTeX.TeX import TeX

@pytest.mark.parametrize('imager_tuple', 
        [('pdf2svg', '.svg', 'vector-imager'),
         ('dvipng', '.png', 'imager')],
        ids=lambda p: p[0])
def test_imager(imager_tuple, tmpdir):
    imager, ext, kind = imager_tuple
    tmpdir = Path(tmpdir) # for old pythons

    tex = TeX()
    tex.ownerDocument.config['images'][kind] = imager
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

    benchfile = root/'benchmarks'/(imager + ext)
    if benchfile.exists():
        bench = benchfile.read_bytes()
        output = outfile.read_bytes()
    else:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/outfile.name))
        raise OSError('No benchmark file: %s' % benchfile)

    if bench != output:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/outfile.name))
        assert False, 'Differences were found'
