import os

from plasTeX.TeX import TeX
from plasTeX.TeX import TeXDocument
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Config import config
from plasTeX.Renderers.HTML5.Config import config as html5_config


def test_package_resource(tmpdir):
	doc = TeXDocument(config=config+html5_config)
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
