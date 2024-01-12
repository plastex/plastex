from pathlib import Path
import re

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
    html_text = html.read_text()
    text = re.sub('id="[^"]*"', '', html_text)
    bench = re.sub('id="[^"]*"', '', html_bench.read_text())
    if text.strip() != bench.strip():
        path = Path(__file__).parent/'new.html'
        print(f'Writing new output to {path}.')
        path.write_text(html_text)
    assert text.strip() == bench.strip()
    assert css.exists()
    css_text = css.read_text()
    css_bench_text = css_bench.read_text()
    if css_text != css_bench_text:
        path = Path(__file__).parent/'new.css'
        print(f'Writing new output to {path}.')
        path.write_text(css_text)
    assert css.read_text() == css_bench.read_text()
