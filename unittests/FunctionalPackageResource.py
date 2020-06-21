import os
from pathlib import Path

from plasTeX.TeX import TeX
from plasTeX.TeX import TeXDocument
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Config import defaultConfig
from plasTeX.Renderers.HTML5.Config import addConfig


def test_package_resource(tmpdir):
    config = defaultConfig()
    config['general'].data['packages-dirs'].value = [str(Path(__file__).parent)]
    addConfig(config)
    doc = TeXDocument(config=config)
    tex = TeX(doc)
    tex.input("""
            \\documentclass{article}
            \\usepackage{examplePackage}
            \\begin{document}
            \\emph{Hello}
            \\end{document}""")

    doc = tex.parse()
    doc.userdata['working-dir'] = os.path.dirname(__file__)

    with tmpdir.as_cwd():
            Renderer().render(doc)

    assert tmpdir.join('styles', 'test.css').isfile()
    assert tmpdir.join('js', 'test.js').isfile()
    assert 'class="em"' in tmpdir.join('index.html').read()
    assert doc.userdata['testing'] == 'test'
