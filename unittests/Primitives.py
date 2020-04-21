from plasTeX.TeX import TeX

def test_expandafter():
    t = TeX().input(r'\def\a[#1]{Argument is #1!}\def\args{[FOO]}\expandafter\a\args')
    assert t.parse().textContent == 'Argument is FOO!'
