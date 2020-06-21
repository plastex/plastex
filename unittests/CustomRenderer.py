import os, sys
import subprocess
from pathlib import Path

plastex_dir = str(Path(__file__).absolute().parent.parent)
sys.path.append(plastex_dir)

def test_custom_renderer(tmpdir):
    try:
        tmpdir = Path(tmpdir)
    except:
        tmpdir = Path(str(tmpdir))

    (tmpdir / "CustomRenderer").mkdir()
    (tmpdir / "CustomRenderer" / "__init__.py").write_text(r"""
from plasTeX.Renderers import Renderer as BaseRenderer

class Renderer(BaseRenderer):
    def  __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        def render(obj):
            return "Test Renderer"

        self["default-layout"] = render
    """)

    (tmpdir / "test.tex").write_text(r"""
\documentclass{article}
\begin{document}
\end{document}
""")

    plastex = str(Path(__file__).parent.parent / "plasTeX" / "plastex")

    os.environ["PYTHONPATH"] = plastex_dir
    # We check the return code manually instead of setting check=True for more
    # readable error
    ret = subprocess.run([plastex, "--renderer=CustomRenderer", "test.tex"], cwd=str(tmpdir), check=False)
    assert ret.returncode == 0

    result = (tmpdir / "test" / "index").read_text()
    assert result == "Test Renderer"

def test_plugin_renderer(tmpdir):
    tmpdir = Path(str(tmpdir))
    (tmpdir/'my_plugin'/'Renderers'/'my_renderer').mkdir(parents=True)
    (tmpdir/'my_plugin'/'Renderers'/'my_renderer'/'__init__.py').write_text(
    r"""from plasTeX.Renderers import Renderer as BaseRenderer

class Renderer(BaseRenderer):
    def  __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        def render(obj):
            return "Test Renderer"

        self["default-layout"] = render
    """)

    (tmpdir / "test.tex").write_text(r"""
\documentclass{article}
\begin{document}
\end{document}
""")
    plastex = str(Path(__file__).parent.parent/'plasTeX'/'plastex')

    ppath = ':'.join(sys.path + [str(tmpdir)])
    env = os.environ
    env['PYTHONPATH'] = ppath
    # We check the return code manually instead of setting check=True for more
    # readable error
    ret = subprocess.run([plastex, "--plugins=my_plugin",
                          "--renderer=my_renderer", "test.tex"],
                         cwd=str(tmpdir), check=False, env=env)
    assert ret.returncode == 0

    result = (tmpdir/'test'/'index').read_text()
    assert result == "Test Renderer"
