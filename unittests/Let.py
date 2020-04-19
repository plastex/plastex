from plasTeX.TeX import TeX

def test_let_redef():
    tex = TeX()
    tex.input(r'''
\newcommand\foo{a}
\let\bar\foo
\renewcommand\foo{b}
\bar
''')
    assert tex.parse().textContent.strip() == "a"

def test_let_nonrecursive():
    tex = TeX()
    tex.input(r'''
\newcommand\foo{a}
\newcommand\fooo{\foo}
\let\bar\fooo
\renewcommand\foo{b}
\bar
''')
    assert tex.parse().textContent.strip() == "b"

def test_let_recursive():
    tex = TeX()
    tex.input(r'''
\newcommand\foo{a}
\let\fooo\foo
\let\bar\fooo
\renewcommand\foo{b}
\bar
''')
    assert tex.parse().textContent.strip() == "a"

def test_let_scope():
    tex = TeX()
    tex.input(r'''
{
   \let\foo=a
   \foo%
}%
\let\foo=b%
\foo
''')
    assert tex.parse().textContent.strip() == "ab"
