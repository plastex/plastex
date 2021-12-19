import sys
import os
from pathlib import Path
from pathlib import Path
from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Context import Context
from plasTeX.Renderers.PageTemplate import Renderer

def test_templates_dir(tmpdir):
    doc = TeXDocument()
    tmpdir = Path(tmpdir)
    extras = tmpdir/'templates'
    extras.mkdir()
    (extras/'my_quotes.jinja2s').write_text("""
name: quote
<div class="quote">{{ obj }}</div>""")
    doc.config['general'].data['extra-templates'].value = [str(extras)]
    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \begin{document}
          \begin{quote}Cogito ergo sum.\end{quote}
        \end{document}
        """)
    renderer = Renderer()
    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    text = (tmpdir/'index.xml').read_text()
    os.chdir(cwd)
    assert '<div class="quote">' in text

def test_theme_dir(tmpdir):
    doc = TeXDocument()
    tmpdir = Path(tmpdir)
    extras = tmpdir/'templates'
    theme = extras/'Themes'/'my_theme'
    theme.mkdir(parents=True)
    (theme/'default-layout.jinja2').write_text("Yo.")
    doc.config['general'].data['extra-templates'].value = [str(extras)]
    doc.config['general'].data['theme'].value = 'my_theme'
    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \begin{document}
          Cogito ergo sum.
        \end{document}
        """)
    renderer = Renderer()
    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    renderer.render(tex.parse())
    text = (tmpdir/'index.xml').read_text()
    os.chdir(cwd)
    assert text == 'Yo.'
