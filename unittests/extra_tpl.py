from pathlib import Path
import os

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Renderers.HTML5 import Renderer


def test_extra_tpl(tmpdir):
    tmpdir = Path(str(tmpdir))
    (tmpdir/'templates').mkdir()

    (tmpdir/'templates'/'Quotations.jinja2s').write_text(
    r"""
name: quote
<div class="test_quote">{{ obj }}</div>
""")
    doc = TeXDocument()
    doc.config['general'].data['extra-templates'].value = [str(tmpdir/'templates')]
    doc.userdata['working-dir'] = str(tmpdir)
    cwd = os.getcwd()
    os.chdir(tmpdir)

    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}

        \begin{document}
        \begin{quote}Test.\end{quote}
        \end{document} """)
    tex.parse()
    renderer = Renderer()
    renderer.render(doc)
    os.chdir(cwd)
    out = (tmpdir/'index.html').read_text()

    assert '<div class="test_quote">' in out

def test_extra_theme(tmpdir):
    tmpdir = Path(str(tmpdir))
    (tmpdir/'templates'/'Themes'/'extreme').mkdir(parents=True)

    (tmpdir/'templates'/'Themes'/'extreme'/'default-layout.jinja2').write_text(
        'This is really minimal theme.')
    doc = TeXDocument()
    doc.config['general'].data['extra-templates'].value = [str(tmpdir/'templates')]
    doc.config['general']['theme'] = 'extreme'
    doc.userdata['working-dir'] = str(tmpdir)

    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}

        \begin{document}
        This content is useless.
        \end{document} """)
    tex.parse()

    cwd = os.getcwd()
    os.chdir(tmpdir)
    renderer = Renderer()
    renderer.render(doc)
    os.chdir(cwd)
    out = (tmpdir/'index.html').read_text()

    assert out == 'This is really minimal theme.'
