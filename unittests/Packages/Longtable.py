#!/usr/bin/env python

import unittest, re, os, tempfile, shutil
from plasTeX.TeX import TeX
from unittest import TestCase
from BeautifulSoup import BeautifulSoup as Soup

class Longtables(TestCase):

    def runDocument(self, content):
        """
        Compile a document with the given content

        Arguments:
        content - string containing the content of the document

        Returns: TeX document

        """
        tex = TeX()
        tex.disableLogging()
        tex.input(r'''\document{article}\usepackage{longtable}\begin{document}%s\end{document}''' % content)
        return tex.parse()

    def runTable(self, content):
        """
        This method compiles and renders a document fragment and 
        returns the result

        Arguments:
        content - string containing the document fragment
      
        Returns: content of output file

        """
        # Create document file
        document = r'\documentclass{article}\usepackage{longtable}\begin{document}%s\end{document}' % content
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

        return Soup(output).find('table', 'tabular')

    def testSimple(self):
        # Table with no bells or whistles
        out = self.runTable(r'''\begin{longtable}{lll} 1 & 2 & 3 \\ a & b & c \\\end{longtable}''')

        numrows = len(out.findAll('tr'))
        assert numrows == 2, 'Wrong number of rows (expecting 2, but got %s): %s' % (numrows, out)

        numcols = len(out.findAll('tr')[0].findAll('td'))
        assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s): %s' % (numcols, out)
        
        numcols = len(out.findAll('tr')[1].findAll('td'))
        assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s): %s' % (numcols, out)
        

    def testHeaders(self):
        headers = [
            r'M & N & O \\\endhead',
            r'M & N & O \\\endfirsthead',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead',
            r'M & N & O \\\endfirsthead\n\\\endhead',
        ]

        # Each header pattern should return the same result
        for header in headers:
            out = self.runTable(r'''\begin{longtable}{lll} %s 1 & 2 & 3 \\ a & b & c \\\end{longtable}''' % header)

            numrows = len(out.findAll('tr'))
            assert numrows == 3, 'Wrong number of rows (expecting 3, but got %s) - %s - %s' % (numrows, header, out)

            headercells = out.findAll('tr')[0].findAll('th')
            numcols = len(headercells)
            assert numcols, 'No header cells found'
            assert numcols == 3, 'Wrong number of headers (expecting 3, but got %s) - %s - %s' % (numcols, header, out)
            text = [x.p.string.strip() for x in headercells]
            assert text[0]=='M','Cell should contain M, but contains %s' % text[0]
            assert text[1]=='N','Cell should contain N, but contains %s' % text[1]
            assert text[2]=='O','Cell should contain O, but contains %s' % text[2]
        
            numcols = len(out.findAll('tr')[1].findAll('td'))
            assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s) - %s - %s' % (numcols, header, out)

    def testFooters(self):
        footers = [
           # Test \endfoot
            r'M & N & O \\\endhead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead F & G & H \\\endfoot',
            r'M & N & O \\\endhead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead F & G & H \\\endfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead F & G & H \\\endfoot',

            # Test \endlastfoot
            r'M & N & O \\\endhead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead F & G & H \\\endlastfoot',
            r'M & N & O \\\endhead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead F & G & H \\\endlastfoot',

            # Test both \endfoot and \endlastfoot
            r'M & N & O \\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
            r'M & N & O \\\endfirsthead\n\\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot',
        ]

        # Each footer pattern should return the same result
        for footer in footers:
            out = self.runTable(r'''\begin{longtable}{lll} %s 1 & 2 & 3 \\ a & b & c \\\end{longtable}''' % footer)

            numrows = len(out.findAll('tr'))
            assert numrows == 4, 'Wrong number of rows (expecting 4, but got %s) - %s - %s' % (numrows, header, out)

            headercells = out.findAll('tr')[-1].findAll('th')
            numcols = len(headercells)
            assert numcols, 'No header cells found'
            assert numcols == 3, 'Wrong number of headers (expecting 3, but got %s) - %s - %s' % (numcols, header, out)
            text = [x.p.string.strip() for x in headercells]
            assert text[0]=='F','Cell should contain F, but contains %s' % text[0]
            assert text[1]=='G','Cell should contain G, but contains %s' % text[1]
            assert text[2]=='H','Cell should contain H, but contains %s' % text[2]
        
            numcols = len(out.findAll('tr')[1].findAll('td'))
            assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s) - %s - %s' % (numcols, header, out)

    def testCaptionNodes(self):
        captions = [
            r'\caption{Caption Text}\\',
            r'\caption{Caption Text}\\ A & B & C \\\endfirsthead',
            r'''\caption{Caption Text}\\ A & B & C \\\endfirsthead 
                \caption{Next Caption Text}\\ X & Y & Z \\\endhead''',
        ]

        for caption in captions:
            doc = self.runDocument(r'''\begin{longtable}{lll} %s 1 & 2 & 3 \end{longtable}''' % caption)

            # Make sure that we only have one caption
            caption = doc.getElementsByTagName('caption')
            assert len(caption) == 1, 'Too many captions'
            caption = caption[0]

            # Make sure that the caption node matches the caption on the table
            table = doc.getElementsByTagName('longtable')[0]
            assert caption is not None, 'Caption is empty'
            assert table.caption is not None, 'Table caption is empty'
            assert table.caption is caption, 'Caption does not match table caption'

            # Make sure that the caption is the sibling of the caption
            assert table.previousSibling is caption, 'Previous sibling is not the caption'
            assert caption.nextSibling is table, 'Next sibling is not the table'

            # Make sure that we got the right caption
            text = caption.textContent.strip()
            assert text == 'Caption Text', 'Caption text should be "Caption Text", but is "%s"' % text

    def testKill(self):
        doc = self.runDocument(r'''\begin{longtable}{lll} 1 & 2 & 3 \\ longtext & & \kill\end{longtable}''')

        table = doc.getElementsByTagName('longtable')[0]
        rows = table.getElementsByTagName('ArrayRow')
        assert len(rows) == 1, 'There should be only 1 row, but found %s' % len(rows)
        content = re.sub(r'\s+', r' ', rows[0].textContent.strip())
        assert content == '1 2 3', 'Content should be "1 2 3", but is %s' % content
        

if __name__ == '__main__':
    unittest.main()

