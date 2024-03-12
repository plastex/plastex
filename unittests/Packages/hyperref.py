from pathlib import Path

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import defaultConfig
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Renderers.HTML5.Config import addConfig

def test_href_no_char_sub():
    """Test for issue #342"""
    tex = TeX()
    tex.input(r'''
\documentclass{article}
\usepackage{hyperref}
\begin{document}
    \href{a--file.pdf}{View file --}.

    A bit of text -- like that.
\end{document}
''')

    hrefs = tex.parse().getElementsByTagName('href')

    assert len(hrefs) == 1
    assert hrefs[0].attributes['url'].textContent == 'a--file.pdf'

def test_hyperref_html5(tmpdir):
    """ Test for issue #316 """

    root = Path(__file__).parent
    config = defaultConfig()
    addConfig(config)
    config['files']['split-level'] = -100
    tex = TeX(TeXDocument(config=config))
    tex.input(r"""
\documentclass{article}
\usepackage{hyperref}

\begin{document}
A link to:

\hyperref[numbered]{numbered section}

\hyperref[not-numbered]{not numbered section}

\section{Numbered}\label{numbered}

This section is numbered.

\section*{Not numbered}\label{not-numbered}

This section is not numbered.

\end{document}
    """)
    doc = tex.parse()
    doc.userdata['working-dir'] = Path(__file__).parent

    with tmpdir.as_cwd():
            Renderer().render(doc)

    assert (Path(tmpdir)/'index.html').exists()

    html = (Path(tmpdir)/'index.html').read_text()

    assert '<a href="index.html#numbered" >numbered section</a>' in html
    assert '<a href="index.html#not-numbered" >not numbered section</a>' in html
