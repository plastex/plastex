from pytest import fixture

from plasTeX.TeX import TeX

@fixture
def node():
    s = TeX()
    s.input(r'\texttt{hi}')
    return s.parse().childNodes[0]

def test_no_style(node):
    style = node.style.inline
    assert style is None

def test_empty_style(node):
    node.style['width'] = ''
    style = node.style.inline
    assert style is None

def test_one_style(node):
    node.style['width'] = '100%'
    style = node.style.inline
    assert style == 'width:100%'

def test_two_styles(node):
    node.style['width'] = '100%'
    node.style['height'] = '100%'
    style = node.style.inline
    assert style == 'width:100%; height:100%'

def test_empty_style_excluded(node):
    node.style['width'] = ''
    node.style['height'] = '100%'
    style = node.style.inline
    assert style == 'height:100%'
