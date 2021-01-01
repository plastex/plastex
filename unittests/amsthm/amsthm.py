from pathlib import Path

from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Config import defaultConfig
from plasTeX.Renderers.HTML5 import Renderer
from plasTeX.Renderers.HTML5.Config import addConfig


def test_amsthm(tmpdir):
    root = Path(__file__).parent
    config = defaultConfig()
    addConfig(config)
    config['files']['split-level'] = -100
    tex = TeX(TeXDocument(config=config))
    tex.input((root/'source.tex').read_text())
    doc = tex.parse()
    doc.userdata['working-dir'] = Path(__file__).parent

    with tmpdir.as_cwd():
            Renderer().render(doc)

    css = Path(tmpdir)/'styles'/'amsthm.css'
    css_bench = root/'benchmark.css'
    html = Path(tmpdir)/'index.html'
    html_bench = root/'benchmark.html'
    assert html.exists()
    assert html.read_text() == html_bench.read_text()
    assert css.exists()
    assert css.read_text() == css_bench.read_text()
