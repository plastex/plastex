from unittest.mock import Mock

from plasTeX.TeX import TeX


def test_xr(monkeypatch):
    mock_load = Mock()
    mock_load.return_value = {'HTML5': {'eq:rfl': {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'index.html#eq:rfl'}}}
    monkeypatch.setattr('plasTeX.Packages.xr.load_paux', mock_load)
    tex = TeX()
    tex.input(r"""
\documentclass{article}

\usepackage{xr}

\externaldocument{toto}

\begin{document}
\ref{eq:rfl}
\end{document}
     """)
    doc = tex.parse()
    mock_load.assert_called_once()
    assert doc.getElementsByTagName('ref')
    ref = doc.getElementsByTagName('ref')[0]

    assert ref.idref['label'] == {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'index.html#eq:rfl'}

def test_xr_prefix(monkeypatch):
    mock_load = Mock()
    mock_load.return_value = {'HTML5': {'eq:rfl': {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'index.html#eq:rfl'}}}
    monkeypatch.setattr('plasTeX.Packages.xr.load_paux', mock_load)
    tex = TeX()
    tex.input(r"""
\documentclass{article}

\usepackage{xr}

\externaldocument[toto-]{toto}

\begin{document}
\ref{toto-eq:rfl}
\end{document}
     """)
    doc = tex.parse()
    mock_load.assert_called_once()
    assert doc.getElementsByTagName('ref')
    ref = doc.getElementsByTagName('ref')[0]

    assert ref.idref['label'] == {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'index.html#eq:rfl'}

def test_xr_prefix_url(monkeypatch):
    mock_load = Mock()
    mock_load.return_value = {'HTML5': {'eq:rfl': {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'index.html#eq:rfl'}}}
    monkeypatch.setattr('plasTeX.Packages.xr.load_paux', mock_load)
    tex = TeX()
    tex.input(r"""
\documentclass{article}

\usepackage{xr}

\externaldocument[toto-]{toto}[myurl/toto/]

\begin{document}
\ref{toto-eq:rfl}
\end{document}
     """)
    doc = tex.parse()
    mock_load.assert_called_once()
    assert doc.getElementsByTagName('ref')
    ref = doc.getElementsByTagName('ref')[0]

    assert ref.idref['label'] == {'ref': '1', 'captionName': 'Equation', 'id': 'eq:rfl', 'url': 'myurl/toto/index.html#eq:rfl'}

