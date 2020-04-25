import re

from pytest import mark


def testSimple(tmpdir, renderXHTML, make_document):
    # Table with no bells or whistles

    doc = make_document(
        packages='longtable',
        content=r'''\begin{longtable}{lll} 1 & 2 & 3 \\ a & b & c \\\end{longtable}''')
    out = renderXHTML(tmpdir, doc).find('table', 'tabular')

    numrows = len(out.findAll('tr'))
    assert numrows == 2, 'Wrong number of rows (expecting 2, but got %s): %s' % (
        numrows, out)

    numcols = len(out.findAll('tr')[0].findAll('td'))
    assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s): %s' % (
        numcols, out)

    numcols = len(out.findAll('tr')[1].findAll('td'))
    assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s): %s' % (
        numcols, out)


@mark.parametrize(
    'header',
    [r'M & N & O \\\endhead',
     r'M & N & O \\\endfirsthead',
     r'M & N & O \\\endfirsthead\n X & Y & Z \\\endhead',
     r'M & N & O \\\endfirsthead\n\\\endhead'])
def testHeaders(header, tmpdir, renderXHTML, make_document):
    # Each header pattern should return the same result
    doc = make_document(
        packages='longtable',
        content=r'''\begin{longtable}{lll} %s 1 & 2 & 3 \\ a & b & c \\\end{longtable}''' % header)

    out = renderXHTML(tmpdir, doc).find('table', 'tabular')

    numrows = len(out.findAll('tr'))
    assert numrows == 3, 'Wrong number of rows (expecting 3, but got %s) - %s - %s' % (
        numrows, header, out)

    headercells = out.findAll('tr')[0].findAll('th')
    numcols = len(headercells)
    assert numcols, 'No header cells found'
    assert numcols == 3, 'Wrong number of headers (expecting 3, but got %s) - %s - %s' % (
        numcols, header, out)
    text = [x.p.string.strip() for x in headercells]
    assert text[0] == 'M', 'Cell should contain M, but contains %s' % text[0]
    assert text[1] == 'N', 'Cell should contain N, but contains %s' % text[1]
    assert text[2] == 'O', 'Cell should contain O, but contains %s' % text[2]

    numcols = len(out.findAll('tr')[1].findAll('td'))
    assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s) - %s - %s' % (
        numcols, header, out)


@mark.parametrize(
    'footer',
    [r'M & N & O \\\endhead F & G & H \\\endfoot',
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
     r'M & N & O \\\endfirsthead\n\\\endhead I & J & K \\\endfoot F & G & H \\\endlastfoot'])
def testFooters(footer, tmpdir, renderXHTML, make_document):
    doc = make_document(
        packages='longtable',
        content=r'''\begin{longtable}{lll} %s 1 & 2 & 3 \\ a & b & c \\\end{longtable}''' % footer)
    out = renderXHTML(tmpdir, doc).find('table', 'tabular')

    numrows = len(out.findAll('tr'))
    assert numrows == 4, 'Wrong number of rows (expecting 4, but got %s) - %s - %s' % (
        numrows, header, out)

    headercells = out.findAll('tr')[-1].findAll('th')
    numcols = len(headercells)
    assert numcols, 'No header cells found'
    assert numcols == 3, 'Wrong number of headers (expecting 3, but got %s) - %s - %s' % (
        numcols, header, out)
    text = [x.p.string.strip() for x in headercells]
    assert text[0] == 'F', 'Cell should contain F, but contains %s' % text[0]
    assert text[1] == 'G', 'Cell should contain G, but contains %s' % text[1]
    assert text[2] == 'H', 'Cell should contain H, but contains %s' % text[2]

    numcols = len(out.findAll('tr')[1].findAll('td'))
    assert numcols == 3, 'Wrong number of columns (expecting 3, but got %s) - %s - %s' % (
        numcols, header, out)


@mark.parametrize('caption', [
    r'\caption{Caption Text}\\',
    r'\caption{Caption Text}\\ A & B & C \\\endfirsthead',
    r'''\caption{Caption Text}\\ A & B & C \\\endfirsthead
            \caption{Next Caption Text}\\ X & Y & Z \\\endhead'''])
def testCaptionNodes(caption, tmpdir, renderXHTML, make_document):
    doc = make_document(
        packages='longtable',
        content=r'''\begin{longtable}{lll} %s 1 & 2 & 3 \end{longtable}''' % caption)

    # Make sure the caption has been captured by longtable
    caption = doc.getElementsByTagName('caption')
    assert not caption, 'Too many captions'

    # Make sure that the caption node matches the caption on the table
    table = doc.getElementsByTagName('longtable')[0]
    caption = table.title
    assert caption is not None, 'Caption is empty'
    assert table.title.textContent.strip(
    ) == u'Caption Text', 'Caption does not match table caption'


def testKill(tmpdir, renderXHTML, make_document):
    doc = make_document(
        packages='longtable',
        content=r'''\begin{longtable}{lll} 1 & 2 & 3 \\ longtext & & \kill\end{longtable}''')

    table = doc.getElementsByTagName('longtable')[0]
    rows = table.getElementsByTagName('ArrayRow')
    assert len(rows) == 1, 'There should be only 1 row, but found %s' % len(rows)
    content = re.sub(r'\s+', r' ', rows[0].textContent.strip())
    assert content == '1 2 3', 'Content should be "1 2 3", but is %s' % content
