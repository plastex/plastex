from unittest.mock import Mock

from plasTeX.TeX import TeX

def test_index_entries_are_there():
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      \index{test}
      \index{test2}
      \printindex
      \end{document}
      ''')
    output = tex.parse()
    assert len(output.userdata['index']) == 2

def test_index_grouping():
    tex = TeX()
    tex.input(r'''
    \documentclass{article}
    \makeindex
    \begin{document}
    \index{Abc!a}\index{Bbcd}\index{Abc!b}\index{Cdd}
    \printindex
    \end{document}
    ''')
    output = tex.parse()
    assert len(output.userdata['links']['index']) == 3

def test_index_sorting():
    tex = TeX()
    tex.input(r'''
    \documentclass{article}
    \makeindex
    \begin{document}
    \index{0@$\to$}\index{0@$\in$}
    \printindex
    \end{document}
    ''')
    output = tex.parse()
    assert len(output.userdata['links']['index']) == 2

