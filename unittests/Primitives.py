from plasTeX.TeX import TeX

def test_expandafter():
    t = TeX().input(r'\def\a[#1]{Argument is #1!}\def\args{[FOO]}\expandafter\a\args')
    assert t.parse().textContent == 'Argument is FOO!'

def test_expandafter_undefined():
    t = TeX().input(r'\def\xx{\yy}\expandafter\def\xx{a}\yy')
    assert t.parse().textContent == 'a'

def test_expandafter_def_csname():
    t = TeX().input(r'\expandafter\def\csname xx\endcsname{a}\xx')
    assert t.parse().textContent == 'a'

def test_expandafter_let_csname():
    t = TeX().input(r'\expandafter\let\csname xx\endcsname=a\xx')
    assert t.parse().textContent == 'a'
