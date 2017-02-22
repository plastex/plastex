import os
import subprocess
from bs4 import BeautifulSoup 
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from pytest import mark, fixture

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import config
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Renderers.HTML5.Config import config as html5_config


config = config + html5_config

@fixture
def renderer():
    return Renderer()

@fixture
def document():
    def doc_fun(compiler=None, converter=None, template=None):
        conf = config.copy()
        if compiler:
            conf['html5']['tikz-compiler'] = compiler
        if converter:
            conf['html5']['tikz-converter'] = converter
        if template:
            conf['html5']['tikz-template'] = template

        doc = TeXDocument(config=conf)
        tex = TeX(doc)
        tex.input("\\documentclass{article}\\usepackage{tikz}\n\\begin{document}\\begin{tikzpicture}\draw (0,0) -- (1,0);\\end{tikzpicture}\n\\end{document}")
        doc = tex.parse()
        doc.userdata['working-dir'] = '.'
        doc.rendererdata['html5'] = {}
        return doc
    return doc_fun


@fixture
def document_cd():
    def doc_fun(compiler=None, converter=None, template=None):
        conf = config.copy()
        if compiler:
            conf['html5']['tikz-compiler'] = compiler
        if converter:
            conf['html5']['tikz-converter'] = converter
        if template:
            conf['html5']['tikz-cd-template'] = template

        doc = TeXDocument(config=conf)
        tex = TeX(doc)
        tex.input("\\documentclass{article}\\usepackage{tikz-cd}\n\\begin{document}\\begin{tikzcd}A \\rar  & B\\end{tikzcd}\n\\end{document}")
        doc = tex.parse()
        doc.userdata['working-dir'] = '.'
        doc.rendererdata['html5'] = {}
        return doc
    return doc_fun


def test_tikz_basic_setup(monkeypatch, tmpdir, document):
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    mock_call = Mock()
    mock_move = Mock()
    monkeypatch.setattr('subprocess.call', mock_call)
    monkeypatch.setattr('os.remove', Mock)
    monkeypatch.setattr('shutil.move', mock_move)

    doc = document()
    tikz_tmpdir = doc.userdata['tikzpicture']['tmp_dir']
    os.chdir(str(tmpdir))
    renderer = Renderer()
    renderer.render(doc)

    pics = doc.getElementsByTagName('tikzpicture')
    assert pics
    tex_path = os.path.join(tikz_tmpdir, pics[0].id + '.tex')
    assert os.path.isfile(tex_path)
    with open(tex_path, 'r') as f:
        assert 'draw' in f.read()

    assert 'pdflatex' in mock_call.call_args_list[0][0][0]
    assert 'pdf2svg' in mock_call.call_args_list[1][0][0]
    assert mock_move.called

    assert 'TikZ picture' in tmpdir.join('index.html').read()
    os.chdir(cur_dir)


def test_tikz_config_options(monkeypatch, tmpdir, document):
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    mock_call = Mock()
    mock_move = Mock()
    monkeypatch.setattr('subprocess.call', mock_call)
    monkeypatch.setattr('os.remove', Mock)
    monkeypatch.setattr('shutil.move', mock_move)

    doc = document(compiler='xelatex', converter='mockconv', template='tikztemplate')
    tikz_tmpdir = doc.userdata['tikzpicture']['tmp_dir']
    os.chdir(str(tmpdir))
    renderer = Renderer()
    renderer.render(doc)
    pics = doc.getElementsByTagName('tikzpicture')
    assert pics
    tex_path = os.path.join(tikz_tmpdir, pics[0].id + '.tex')
    assert os.path.isfile(tex_path)
    with open(tex_path, 'r') as f:
        assert 'usetikzlibrary' in f.read()

    assert 'xelatex' in mock_call.call_args_list[0][0][0]
    assert 'mockconv' in mock_call.call_args_list[1][0][0]
    os.chdir(cur_dir)

def test_tikzcd_basic_setup(monkeypatch, tmpdir, document_cd):
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    mock_call = Mock()
    mock_move = Mock()
    monkeypatch.setattr('subprocess.call', mock_call)
    monkeypatch.setattr('os.remove', Mock)
    monkeypatch.setattr('shutil.move', mock_move)

    doc = document_cd()
    tikz_tmpdir = doc.userdata['tikzcd']['tmp_dir']
    os.chdir(str(tmpdir))
    renderer = Renderer()
    renderer.render(doc)

    pics = doc.getElementsByTagName('tikzcd')
    assert pics
    tex_path = os.path.join(tikz_tmpdir, pics[0].id + '.tex')
    assert os.path.isfile(tex_path)
    with open(tex_path, 'r') as f:
        assert '\\rar' in f.read()

    assert 'pdflatex' in mock_call.call_args_list[0][0][0]
    assert 'pdf2svg' in mock_call.call_args_list[1][0][0]
    assert mock_move.called

    assert 'Commutative diagram' in tmpdir.join('index.html').read()
    os.chdir(cur_dir)

def test_tikzcd_config_options(monkeypatch, tmpdir, document_cd):
    cur_dir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    mock_call = Mock()
    mock_move = Mock()
    monkeypatch.setattr('subprocess.call', mock_call)
    monkeypatch.setattr('os.remove', Mock)
    monkeypatch.setattr('shutil.move', mock_move)

    doc = document_cd(compiler='xelatex', converter='mockconv', template='tikzcdtemplate')
    tikz_tmpdir = doc.userdata['tikzcd']['tmp_dir']
    os.chdir(str(tmpdir))
    renderer = Renderer()
    renderer.render(doc)
    pics = doc.getElementsByTagName('tikzcd')
    assert pics
    tex_path = os.path.join(tikz_tmpdir, pics[0].id + '.tex')
    assert os.path.isfile(tex_path)
    with open(tex_path, 'r') as f:
        assert 'usetikzlibrary' in f.read()

    assert 'xelatex' in mock_call.call_args_list[0][0][0]
    assert 'mockconv' in mock_call.call_args_list[1][0][0]
    os.chdir(cur_dir)

def test_functional(tmpdir):
    cur_dir = os.getcwd()
    tmpdir.join('test.tex').write("""
    \documentclass{article} 
    \usepackage{tikz, tikz-cd}

    \\begin{document}
    \\begin{tikzpicture}
            \draw (0, 0) -- (1, 0);
    \end{tikzpicture}

    \\begin{tikzcd}
            A \\rar & B
    \end{tikzcd}
    \end{document}""")
    os.chdir(str(tmpdir))
    subprocess.call(
            ['plastex', '--renderer', 'HTML5', str(tmpdir.join('test.tex'))])
    assert os.path.isdir(str(tmpdir.join('test')))
    assert os.path.isfile(str(tmpdir.join('test', 'index.html')))
    soup = BeautifulSoup(tmpdir.join('test', 'index.html').read(), "html.parser")
    svgs = soup.findAll('object')
    for svg in svgs:
            assert os.path.isfile(str(tmpdir.join('test', svg.attrs['data'])))

    os.chdir(cur_dir)
