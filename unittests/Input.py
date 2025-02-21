from pathlib import Path
from plasTeX.TeX import TeX
from plasTeX import Command
import contextlib
import os
import textwrap
import pytest


@contextlib.contextmanager
def local_env_var(name, value):
    try:
        old = os.environ[name]
    except KeyError:
        os.environ[name] = value
        try:
            yield
        finally:
            del os.environ[name]
    else:
        os.environ[name] = value
        try:
            yield
        finally:
            os.environ[name] = old


class foo(Command):
    def invoke(self, tex):
        self.data = tex.currentInput[0].filename

def test_input(tmpdir):
    with tmpdir.as_cwd():
        Path("input.tex").write_text(r'''
\documentclass{article}
\begin{document}
\input{input2}
\end{document}
''')
        Path("input2.tex").write_text(r'\foo')

        tex = TeX(file="input.tex")
        tex.ownerDocument.context.contexts[0]["foo"] = foo

        assert "./input2.tex" == tex.parse().getElementsByTagName("foo")[0].data

def test_input_without_kpsewhich(tmpdir):
    with tmpdir.as_cwd():
        Path("input.tex").write_text(r'''
\documentclass{article}
\begin{document}
\input{input2.tex}
\end{document}
''')
        Path("input2.tex").write_text(r'\foo')

        tex = TeX(file="input.tex")
        tex.ownerDocument.context.contexts[0]["foo"] = foo
        tex.ownerDocument.config['general']['kpsewhich'] = ''

        assert "./input2.tex" == tex.parse().getElementsByTagName("foo")[0].data


@pytest.mark.parametrize('without_kpsewhich', [False, True])
def test_input_nested_path(tmp_path, without_kpsewhich):
    (tmp_path / "input.tex").write_text(textwrap.dedent(r'''
        \documentclass{article}
        \begin{document}
        \input{nested/input2.tex}
        \end{document}
        '''))
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "input2.tex").write_text(r'\foo')

    # deliberately test the case where the working directory is elsewhere
    with local_env_var("TEXINPUTS", str(tmp_path)):
        tex = TeX(file="input.tex")
        tex.ownerDocument.context.contexts[0]["foo"] = foo
        if without_kpsewhich:
            tex.ownerDocument.config['general']['kpsewhich'] = ''

        assert str(tmp_path / "nested" / "input2.tex") == tex.parse().getElementsByTagName("foo")[0].data


@pytest.mark.parametrize('without_kpsewhich', [False, True])
def test_input_absolute_path(tmp_path, without_kpsewhich):
    (tmp_path / "input.tex").write_text(textwrap.dedent(r'''
        \documentclass{article}
        \begin{document}
        \input{''' + str(tmp_path / "input2.tex") + r'''}
        \end{document}
        '''))
    (tmp_path / "input2.tex").write_text(r'\foo')

    tex = TeX(file=str(tmp_path / "input.tex"))
    tex.ownerDocument.context.contexts[0]["foo"] = foo
    if without_kpsewhich:
        tex.ownerDocument.config['general']['kpsewhich'] = ''

    assert str(tmp_path / "input2.tex") == tex.parse().getElementsByTagName("foo")[0].data


def test_input_without_kpsewhich_without_extension(tmpdir):
    with tmpdir.as_cwd():
        Path("input.tex").write_text(r'''
\documentclass{article}
\begin{document}
\input{input2}
\end{document}
''')
        Path("input2.tex").write_text(r'\foo')

        tex = TeX(file="input.tex")
        tex.ownerDocument.context.contexts[0]["foo"] = foo
        tex.ownerDocument.config['general']['kpsewhich'] = ''

        assert "./input2.tex" == tex.parse().getElementsByTagName("foo")[0].data
