import pytest

from plasTeX.TeX import TeX, TeXDocument

@pytest.mark.parametrize("doc_class", ['article', 'report', 'book'])
def test_load_class(doc_class):
    doc = TeXDocument()
    tex = TeX(doc)
    doc.context.loadPackage(tex, doc_class)
