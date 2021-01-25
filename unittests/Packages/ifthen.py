from plasTeX.Packages.ifthen import *

def test_ifthenelse_num_lessthan(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{1<5}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{5<1}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_num_greaterthan(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{1>5}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)
    text = '''\\ifthenelse{5>1}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)

def test_ifthenelse_num_equal(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{5=5}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{5=1}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_num_def(tmpdir, renderXHTML, make_document):
    text = '''\\def\\foo{5}\\ifthenelse{\\foo=5}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\def\\foo{5}\\ifthenelse{\\foo=1}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_isodd(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\isodd{5}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\isodd{6}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_isundefined(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\isundefined{\\foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\def\\foo{5}\\ifthenelse{\\isundefined{\\foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_boolean(tmpdir, renderXHTML, make_document):
    text = '''\\newboolean{foo}\\setboolean{foo}{true}\\ifthenelse{\\boolean{foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\newboolean{foo}\\setboolean{foo}{false}\\ifthenelse{\\boolean{foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_provideboolean(tmpdir, renderXHTML, make_document):
    text = '''\\provideboolean{foo}\\setboolean{foo}{true}\\ifthenelse{\\boolean{foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)

def test_ifthenelse_equal(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\equal{foo}{foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\equal{foo}{bar}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_equal_def(tmpdir, renderXHTML, make_document):
    text = '''\\def\\bar{foo}\\ifthenelse{\\equal{\\bar}{foo}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\def\\bar{foo}\\ifthenelse{\\equal{\\bar}{baz}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_lengthtest_lessthan(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\lengthtest{1cm<1in}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\lengthtest{1in<1cm}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_lengthtest_greaterthan(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\lengthtest{1cm>5mm}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\lengthtest{5mm>1cm}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_lengthtest_equal(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\lengthtest{1cm=10mm}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\lengthtest{1cm=11mm}}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_and(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{3>2 \\and 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{3>2 \\AND 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{3>2 \\and 5>40}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)
    text = '''\\ifthenelse{3>20 \\AND 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_or(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{3>2 \\or 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{3>20 \\OR 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{3>20 \\or 5>40}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)
    text = '''\\ifthenelse{3>20 \\OR 5>40}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_not(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{\\not 5>40}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\NOT 5>4}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_parens(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{1>0 \\or \\( 1>0 \\and 0>1 \\)}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-true' in str(output)
    text = '''\\ifthenelse{\\( 1>0 \\or 1>0 \\) \\and 0>1}{ifthen-true}{ifthen-false}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-false' in str(output)

def test_ifthenelse_nested(tmpdir, renderXHTML, make_document):
    text = '''\\ifthenelse{0>1}{foo}{ifthen-\\ifthenelse{1>0}{nested-true}{nested-false}}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-nested-true' in str(output)
    assert 'ifthen-nested-false' not in str(output)
    assert 'foo' not in str(output)
    text = '''\\ifthenelse{0>1}{foo}{ifthen-\\ifthenelse{0>1}{nested-true}{nested-false}}'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert 'ifthen-nested-false' in str(output)
    assert 'ifthen-nested-true' not in str(output)
    assert 'foo' not in str(output)

def test_whiledo(tmpdir, renderXHTML, make_document):
    text = r'''
    \newcounter{foo}
    \setcounter{foo}{1}
    \whiledo{\value{foo}<10}{%
        \arabic{foo}%
        \stepcounter{foo}%
    }'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert '123456789' in str(output)

def test_whiledo_nested(tmpdir, renderXHTML, make_document):
    text = r'''
    \newcounter{foo}
    \setcounter{foo}{1}
    \newcounter{bar}
    \whiledo{\value{foo}<4}{%
        \setcounter{bar}{1}%
        \arabic{foo}%
        \whiledo{\value{bar}<4}{%
            \arabic{bar}%
            \stepcounter{bar}%
        }
        \stepcounter{foo}%
    }'''
    doc = make_document(packages='ifthen', content=text)
    out = doc.getElementsByTagName('document')[0]
    output = renderXHTML(tmpdir, doc)
    assert '1123 2123 3123' in str(output)
