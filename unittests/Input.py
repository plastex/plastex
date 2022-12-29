from pathlib import Path
from plasTeX.TeX import TeX
from plasTeX import Command

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
