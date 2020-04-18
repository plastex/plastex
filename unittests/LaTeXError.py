import os, subprocess
from pathlib import Path

def test_latex_imager_failure(tmpdir, pytestconfig):
    """While rendering using LaTeX in an imager, a missing package shouldn't
    block plasTeX."""
    tmpdir = Path(str(tmpdir))

    (tmpdir / "CustomRenderer").mkdir()
    (tmpdir / "CustomRenderer" / "__init__.py").write_text(r"""
from plasTeX.Renderers import Renderer as BaseRenderer

class Renderer(BaseRenderer):
    def  __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        self["document"] = lambda x: x.image.url
    """)

    (tmpdir/'test.tex').write_text(r"""
    \documentclass{article}
    \usepackage{nonexistentpackage}
    \begin{document}
    \end{document}""")

    cwd = os.getcwd()
    os.chdir(str(tmpdir))

    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
    capmanager.suspend_global_capture(in_=True)

    proc = subprocess.run(['plastex', '--renderer=CustomRenderer', 'test.tex'], timeout=3, check=False)

    capmanager.resume_global_capture()
    os.chdir(cwd)
