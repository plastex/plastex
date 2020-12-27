import sys
from pathlib import Path
from plasTeX.TeX import TeX, TeXDocument
from plasTeX.Context import Context

def test_builtin_packages():
    doc = TeXDocument()
    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \usepackage{float}
        \begin{document}
          \floatstyle{ruled}
        \end{document}
        """)
    tex.parse()
    assert doc.getElementsByTagName('floatstyle')

def test_packages_dirs(tmpdir):
    tmpdir = Path(str(tmpdir))

    (tmpdir / "mypkg.py").write_text(
    r"""
from plasTeX import Command

class mycmd(Command):
    my_var = 'ok'
""")
    doc = TeXDocument()
    doc.config['general'].data['packages-dirs'].value = [str(tmpdir)]


    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \usepackage{mypkg}
        \begin{document}
          \mycmd
        \end{document}
        """)
    tex.parse()
    assert doc.getElementsByTagName('mycmd')
    node = doc.getElementsByTagName('mycmd')[0]
    assert node.my_var == 'ok'


def test_packages_dirs_name_clash(tmpdir):
    tmpdir = Path(str(tmpdir))

    (tmpdir / "plasTeX.py").write_text(
    r"""
from plasTeX import Command

class mycmd(Command):
    my_var = 'ok'
""")
    doc = TeXDocument()
    doc.config['general'].data['packages-dirs'].value = [str(tmpdir)]


    tex = TeX(doc)
    assert not doc.context.loadPackage(tex, 'plasTeX')

def test_plugin_packages(tmpdir):
    tmpdir = Path(str(tmpdir))
    (tmpdir/'my_plugin'/'Packages').mkdir(parents=True)
    (tmpdir/'my_plugin'/'__init__.py').touch()
    (tmpdir/'my_plugin'/'Packages'/'mypkg.py').write_text(
    r"""
from plasTeX import Command

class mycmd(Command):
    my_var = 'ok'
""")
    sys.path.append(str(tmpdir))
    doc = TeXDocument()
    doc.config['general'].data['plugins'].value = ['my_plugin']

    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \usepackage{mypkg}
        \begin{document}
          \mycmd
        \end{document}
        """)
    tex.parse()
    sys.path.pop()
    assert doc.getElementsByTagName('mycmd')
    node = doc.getElementsByTagName('mycmd')[0]
    assert node.my_var == 'ok'


def test_crazy_package_name():
    """
    This test tries to load a package whose name clashes with a name of
    the python standard library and does not exists in plasTeX.
    """
    ctx = Context()
    tex = TeX()
    assert not ctx.loadPackage(tex, 'rlcompleter')
