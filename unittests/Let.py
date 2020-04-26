from helpers.utils import compare_output

def test_let_redef():
    compare_output(r'''
\newcommand\foo{a}
\let\bar\foo
\renewcommand\foo{b}
\bar
''')

def test_let_nonrecursive():
    compare_output(r'''
\newcommand\foo{a}
\newcommand\fooo{\foo}
\let\bar\fooo
\renewcommand\foo{b}
\bar
''')

def test_let_recursive():
    compare_output(r'''
\newcommand\foo{a}
\let\fooo\foo
\let\bar\fooo
\renewcommand\foo{b}
\bar
''')

def test_let_scope():
    compare_output(r'''
{
   \let\foo=a
   \foo%
}%
\let\foo=b%
\foo
''')
