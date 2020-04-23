from helpers.utils import compare_output

def test_expandafter():
    compare_output(r'\def\a[#1]{Argument is #1!}\def\args{[FOO]}\expandafter\a\args')

def test_expandafter_undefined():
    compare_output(r'\def\xx{\yy}\expandafter\def\xx{a}\yy')

def test_expandafter_def_csname():
    compare_output(r'\expandafter\def\csname xx\endcsname{a}\xx')

def test_expandafter_let_csname():
    compare_output(r'\expandafter\let\csname xx\endcsname=a\xx')

def test_expandafter_once():
    compare_output(r'\def\a{ab}\def\b{\a}\def\foo#1{#1.}\expandafter\foo\b')

def test_expandafter_non_macro():
    compare_output(r'\def\foo#1{#1.}\expandafter\foo ab')
