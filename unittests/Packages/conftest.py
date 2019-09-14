import os

# Will try to use obsolete, but good enough for us, BeautifulSoup 3 if
# BeautifulSoup 4 is not available. Need to cope with slight API difference
try:
    from bs4 import BeautifulSoup

    def Soup(source):
        return BeautifulSoup(source, 'html.parser')
except ImportError:
    from BeautifulSoup import BeautifulSoup as Soup

from pytest import fixture

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import config
from plasTeX.Renderers.XHTML import Renderer


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

        doc = TeXDocument(config=config)
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
        os.chdir(str(tmpdir))
        Renderer().render(doc)
        assert tmpdir.join('index.html').isfile()

        # Get output file
        return Soup(tmpdir.join('index.html').read())
    return runRenderer
