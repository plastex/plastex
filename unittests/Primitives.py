from plasTeX.TeX import TeX
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

def test_evil_double_dollars():
    tex = TeX()
    tex.input('$a$$b$')
    nodes = tex.parse().getElementsByTagName('math')
    assert len(nodes) == 2
    assert nodes[0].textContent == 'a'
    assert nodes[1].textContent == 'b'

def test_more_evil_double_dollars():
    tex = TeX()
    tex.input('$a$$$b$$$c$')
    doc = tex.parse()
    mathnodes = doc.getElementsByTagName('math')
    assert len(mathnodes) == 2
    assert mathnodes[0].textContent == 'a'
    assert mathnodes[1].textContent == 'c'
    displaymathnodes = doc.getElementsByTagName('displaymath')
    assert len(displaymathnodes) == 1
    assert displaymathnodes[0].textContent == 'b'

def test_even_more_evil_double_dollars():
    tex = TeX()
    tex.input('$a$$$$$$$b$$')
    doc = tex.parse()
    mathnodes = doc.getElementsByTagName('math')
    assert len(mathnodes) == 1
    assert mathnodes[0].textContent == 'a'
    displaymathnodes = doc.getElementsByTagName('displaymath')
    assert len(displaymathnodes) == 2
    assert displaymathnodes[0].textContent == ''
    assert displaymathnodes[1].textContent == 'b'
