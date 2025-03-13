from plasTeX.TeX import TeX
from plasTeX import TeXDocument
from plasTeX.Config import defaultConfig

def test_charsub():
    config = defaultConfig()

    doc = TeXDocument(config=config)
    tex = TeX(doc)

    p = tex.input(r'''{``'' '---}''').parse()[0]
    p.paragraphs(charsubs=doc.charsubs)
    assert p.textContent == "“” ’—"

def test_modify_charsub():
    config = defaultConfig()
    config["document"]["disable-charsub"] = ["'"]

    doc = TeXDocument(config=config)
    tex = TeX(doc)

    p = tex.input(r'''{``'' '---}''').parse()[0]
    p.paragraphs(charsubs=doc.charsubs)
    assert p.textContent == "“” '—"
