from pathlib import Path
import os
import tempfile
import shutil

from pytest import fixture

from plasTeX.TeX import TeX, TeXDocument

@fixture(scope='module')
def sorting_dir():
    tmpdir = Path(tempfile.mkdtemp())
    (tmpdir/'sorting.bbl').write_text(r"""
        \begin{thebibliography}{2}
        \providecommand{\natexlab}[1]{#1}
        \providecommand{\url}[1]{\texttt{#1}}
        \expandafter\ifx\csname urlstyle\endcsname\relax
        \providecommand{\doi}[1]{doi: #1}\else
        \providecommand{\doi}{doi: \begingroup \urlstyle{rm}\Url}\fi

        \bibitem[Doe(2021{\natexlab{a}})]{Author1}
        J.~Doe.
        \newblock Article of the second author.
        \newblock \emph{Nature}, 2021{\natexlab{a}}.

        \bibitem[Doe(2021{\natexlab{b}})]{Author2}
        J.~Doe.
        \newblock Article of the first author.
        \newblock \emph{Nature}, 2021{\natexlab{b}}.

        \end{thebibliography}""")
    (tmpdir/'sorting.aux').write_text(r"""
        \relax
        \citation{Author1,Author2}
        \citation{Author2,Author1}
        \bibstyle{unsrtnat}
        \bibdata{sorting.bib}
        \bibcite{Author1}{{1}{2021{}}{{Doe}}{{}}}
        \bibcite{Author2}{{2}{2021{}}{{Doe}}{{}}}""")
    yield tmpdir
    shutil.rmtree(tmpdir)

def test_natbib_sorting(sorting_dir):
    doc = TeXDocument()
    old_dir = os.getcwd()
    os.chdir(sorting_dir)
    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \usepackage[numbers, sort]{natbib}
        \begin{document}
        \cite{Author1, Author2} and \cite{Author2, Author1}.
        \bibliographystyle{unsrtnat}
        \bibliography{sorting.bib}
        \end{document}""")
    tex.jobname = 'sorting'
    doc = tex.parse()
    os.chdir(old_dir)

    cites = doc.getElementsByTagName('cite')
    assert len(cites) == 2
    for cite in cites:
        assert [x.id for x in cite.bibitems] == ['Author1', 'Author2']


def test_natbib_nosorting(sorting_dir):
    doc = TeXDocument()
    old_dir = os.getcwd()
    os.chdir(sorting_dir)
    tex = TeX(doc)
    tex.input(r"""
        \documentclass{article}
        \usepackage[numbers]{natbib}
        \begin{document}
        \cite{Author1, Author2} and \cite{Author2, Author1}.
        \bibliographystyle{unsrtnat}
        \bibliography{sorting.bib}
        \end{document}""")
    tex.jobname = 'sorting'
    doc = tex.parse()
    os.chdir(old_dir)

    cites = doc.getElementsByTagName('cite')
    assert len(cites) == 2
    assert [x.id for x in cites[0].bibitems] == ['Author1', 'Author2']
    assert [x.id for x in cites[1].bibitems] == ['Author2', 'Author1']
