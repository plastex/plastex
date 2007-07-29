#!/usr/bin/env python

import unittest, re, os, tempfile, shutil
from plasTeX.TeX import TeX
from unittest import TestCase
from BeautifulSoup import BeautifulSoup as Soup

class Alltt(TestCase):

    def runDocument(self, content):
        """
        Compile a document with the given content

        Arguments:
        content - string containing the content of the document

        Returns: TeX document

        """
        tex = TeX()
        tex.disableLogging()
        tex.input(r'''\document{article}\usepackage{alltt}\begin{document}%s\end{document}''' % content)
        return tex.parse()

    def runPreformat(self, content):
        """
        This method compiles and renders a document fragment and 
        returns the result

        Arguments:
        content - string containing the document fragment
      
        Returns: content of output file

        """
        # Create document file
        document = r'\documentclass{article}\usepackage{alltt}\begin{document}%s\end{document}' % content
        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, 'longtable.tex')
        open(filename, 'w').write(document)

        # Run plastex on the document
        log = os.popen('plastex -d %s %s 2>&1' % (tmpdir, filename)).read()
        assert '[ index.html ]' in log, 'No file was generated - %s' % log

        # Get output file
        output = open(os.path.join(tmpdir, 'index.html')).read()

        # Clean up
        shutil.rmtree(tmpdir)
        os.remove('longtable.paux')

        return Soup(output).findAll('pre')[-1]

    def testSimple(self):
        text = '''\\begin{alltt}\n   line 1\n   line 2\n   line 3\n\\end{alltt}'''
        lines = ['', '   line 1', '   line 2', '   line 3', '']

        # Test text content of node
        out = self.runDocument(text).getElementsByTagName('alltt')[0]

        plines = out.textContent.split('\n')
        assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

        # Test text content of rendering
        out = self.runPreformat(text)

        plines = out.string.split('\n')
        assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)


    def testCommands(self):
        text = '''\\begin{alltt}\n   line 1\n   \\textbf{line} 2\n   \\textit{line 3}\n\\end{alltt}'''
        lines = ['', '   line 1', '   line 2', '   line 3', '']

        # Test text content of node
        out = self.runDocument(text).getElementsByTagName('alltt')[0]

        plines = out.textContent.split('\n')
        assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

        bf = out.getElementsByTagName('textbf')[0]
        assert bf.textContent == 'line', 'Bold text should be "line", but it is "%s"' % bf.textContent

        it = out.getElementsByTagName('textit')[0]
        assert it.textContent == 'line 3', 'Italic text should be "line 3", but it is "%s"' % it.textContent

        # Test rendering
        out = self.runPreformat(text)

        assert out.b.string == 'line', 'Bold text should be "line", but it is "%s"' % out.b.string

        assert out.i.string == 'line 3', 'Italic text should be "line 3", but it is "%s"' % out.i.string


if __name__ == '__main__':
    unittest.main()

