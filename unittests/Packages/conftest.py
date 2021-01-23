import os

from bs4 import BeautifulSoup

from pytest import fixture

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import defaultConfig
from plasTeX.Renderers.XHTML import Renderer

def Soup(source):
    return BeautifulSoup(source, 'html.parser')

@fixture(scope='session')
def make_document():
    def runDocument(packages='', content=''):
        """
        Compile a document with the given content

        Arguments:
        packages - string containing comma separated packages to use
        content - string containing the content of the document

        Returns: TeX document

        """

        doc = TeXDocument(config=defaultConfig())
        tex = TeX(doc)
        tex.disableLogging()
        tex.input(r'''
                \documentclass{article}
                \usepackage{%s}
                \begin{document}%s\end{document}''' % (packages, content))
        doc = tex.parse()
        doc.userdata['working-dir'] = os.path.dirname(__file__)
        return doc
    return runDocument


@fixture(scope='session')
def renderXHTML():
    def runRenderer(tmpdir, doc):
        # Create document file

        # Run plastex on the document
        with tmpdir.as_cwd():
            Renderer().render(doc)

        assert tmpdir.join('index.html').isfile()

        # Get output file
        return Soup(tmpdir.join('index.html').read())
    return runRenderer
