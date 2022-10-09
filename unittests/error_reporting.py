from unittest.mock import Mock
from pytest import raises

from plasTeX.TeX import TeX

def test_error_line_reporting(monkeypatch):
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.Context.log.error', mock_logger)
    tex = TeX()
    tex.input(r'''\documentclass{article}
        \makeatletter
        \makeatother

        \newcommand{}}} % Intentional error
        \begin{document}\end{document}
      ''')
    with raises(IndexError):
        tex.parse()
    assert 'line 5' in ' '.join(mock_logger.call_args[0])

