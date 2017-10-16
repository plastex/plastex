#!/usr/bin/env python

import os 
from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import config
from plasTeX.Renderers.XHTML import Renderer

# Will try to use obsolete, but good enough for us, BeautifulSoup 3 if
# BeautifulSoup 4 is not available. Need to cope with slight API difference
try:
    from bs4  import BeautifulSoup
    def Soup(source):
        return BeautifulSoup(source, 'html.parser')
except ImportError:
    from BeautifulSoup import BeautifulSoup as Soup


def runDocument(content):
    """
    Compile a document with the given content

    Arguments:
    content - string containing the content of the document

    Returns: TeX document

    """
    
    doc = TeXDocument(config=config)
    tex = TeX(doc)
    tex.disableLogging()
    tex.input(r'''\documentclass{article}\usepackage{alltt}\begin{document}%s\end{document}''' % content)
    doc = tex.parse()
    doc.userdata['working-dir'] = os.path.dirname(__file__)
    return doc


def runPreformat(doc, tmpdir):
    """
    This method renders a document in XHTML into tmpdir and
    returns the last pre tag

    Arguments:
    doc - the plasTeX document to render
    tmpdir - the output directory name

    Returns: last pre tag in output

    """
    # Create document file

    # Run plastex on the document
    os.chdir(str(tmpdir))
    Renderer().render(doc)
    assert tmpdir.join('index.html').isfile()

    # Get output file
    output = tmpdir.join('index.html').read()

    return Soup(output).findAll('pre')[-1]

def test_simple(tmpdir):
    text = '''\\begin{alltt}\n   line 1\n   line 2\n   line 3\n\\end{alltt}'''
    lines = ['', '   line 1', '   line 2', '   line 3', '']

    # Test text content of node
    doc = runDocument(text)
    out = doc.getElementsByTagName('alltt')[0]

    plines = out.textContent.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

    # Test text content of rendering
    out = runPreformat(doc, tmpdir)

    plines = out.string.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

def test_commands(tmpdir):
    text = '''\\begin{alltt}\n   line 1\n   \\textbf{line} 2\n   \\textit{line 3}\n\\end{alltt}'''
    lines = ['', '   line 1', '   line 2', '   line 3', '']

    # Test text content of node
    doc = runDocument(text)
    out = doc.getElementsByTagName('alltt')[0]

    plines = out.textContent.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

    bf = out.getElementsByTagName('textbf')[0]
    assert bf.textContent == 'line', 'Bold text should be "line", but it is "%s"' % bf.textContent

    it = out.getElementsByTagName('textit')[0]
    assert it.textContent == 'line 3', 'Italic text should be "line 3", but it is "%s"' % it.textContent

    # Test rendering
    out = runPreformat(doc, tmpdir)

    assert out.b.string == 'line', 'Bold text should be "line", but it is "%s"' % out.b.string

    assert out.i.string == 'line 3', 'Italic text should be "line 3", but it is "%s"' % out.i.string
