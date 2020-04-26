from plasTeX.TeX import TeX
from plasTeX import TeXDocument
from plasTeX.Config import config as base_config

def test_charsub():
    config = base_config.copy()

    doc = TeXDocument(config=config)
    tex = TeX(doc)

    p = tex.input(r'''{``'' '---}''').parse()[0]
    p.paragraphs()
    assert p.textContent == "“” ’—"

def test_modify_charsub():
    config = base_config.copy()
    config["document"]["disable-charsub"] = "'"

    doc = TeXDocument(config=config)
    tex = TeX(doc)

    p = tex.input(r'''{``'' '---}''').parse()[0]
    p.paragraphs()
    assert p.textContent == "“” '—"
