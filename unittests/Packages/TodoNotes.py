from plasTeX.TeX import TeX
from plasTeX.Renderers import Renderer
from pathlib import Path

def test_todo():
    todo = TeX().input(r'\usepackage{todonotes}\todo{123}').parse()[1]
    assert not todo.blockType
    assert todo.attributes["todo"].textContent == "123"

def test_todo_inline():
    todo = TeX().input(r'\usepackage{todonotes}\todo[inline]{123}').parse()[1]
    assert todo.blockType
    assert todo.attributes["todo"].textContent == "123"

def test_todo_disable(tmpdir):
    renderer = Renderer()
    def render_todo(obj):
        if obj.ownerDocument.userdata['todonotes']['disable']:
            return "disabled"
        else:
            return str(obj.attributes["todo"])

    renderer["todo"] = render_todo

    enabled = r'''
\documentclass{article}
\usepackage{todonotes}
\begin{document}
  \todo{foo}
\end{document}
'''

    disabled = r'''
\documentclass{article}
\usepackage[disable]{todonotes}
\begin{document}
  \todo{foo}
\end{document}
'''

    with tmpdir.as_cwd():
        renderer.render(TeX().input(enabled).parse())
        assert Path("index").read_text().strip() == "foo"

        renderer.render(TeX().input(disabled).parse())
        assert Path("index").read_text().strip() == "disabled"
