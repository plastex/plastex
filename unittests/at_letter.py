try:
    from unittest.mock import Mock 
except ImportError:
    from mock import Mock

from plasTeX.TeX import TeX

def test_at_letter_verb(monkeypatch):
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.Context.log.warning', mock_logger)
    tex = TeX()
    tex.input(r'''
      \documentclass{article}
      \begin{document}
      \verb@test@
      \end{document}
      ''')
    output = tex.parse()
    assert mock_logger.call_count == 0

def test_at_letter_newcommand(monkeypatch):
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.Context.log.warning', mock_logger)
    tex = TeX()
    tex.input(r'''
        \documentclass{article}
        \newcommand{\foo}[1]{#1}
        \begin{document}
        \foo@
        \end{document}
      ''')
    output = tex.parse()
    assert mock_logger.call_count == 0
