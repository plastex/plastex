from unittest.mock import Mock
from plasTeX.TeX import TeX

from helpers.utils import compare_output

import pytest

def testTrue():
    compare_output(r'\newif\iffoo\footrue\iffoo hi\else bye\fi')

def testFalse():
    compare_output(r'\newif\iffoo\foofalse\iffoo hi\else bye\fi')

def testIf():
    compare_output(r'\if*! bye\else text\fi\if** one\else two\fi')

def testIfNum():
    compare_output(r'\ifnum 5 < 2 bye\else text\fi\ifnum 2 = 2 one\else two\fi')

def testIfDim():
    compare_output(r'\ifdim -5 pt > 2in bye\else text\fi\ifdim 2mm = 2 mm one\else two\fi')

def testIfOdd():
    compare_output(r'\ifodd 2 bye\else text\fi\ifodd 3 one\else two\fi')

# This is not implemented correctly; it is unconditionally false
@pytest.mark.xfail
def testIfVMode():
    compare_output(r'\ifvmode bye\else text\fi\ifvmode one\else two\fi')

# This is not implemented correctly; it is unconditionally true
@pytest.mark.xfail
def testIfHMode():
    compare_output(r'\ifhmode bye\else text\fi\ifhmode one\else two\fi')

def testIfMMode():
    compare_output(r'\ifmmode bye\else text\fi\ifmmode one\else two\fi')

def testIfInner():
    compare_output(r'\ifinner bye\else text\fi\ifinner one\else two\fi')

def testIfCat():
    compare_output(r'\ifcat!a bye\else text\fi\ifcat!( one\else two\fi')

def testIfX():
    compare_output(r'\ifx!!bye\else text\fi\ifx!( one\else two\fi')

# This is defined to be unconditionally false
@pytest.mark.xfail
def testIfVoid():
    compare_output(r'\ifvoid12 bye\else text\fi\ifvoid16 one\else two\fi')

def testIfHBox():
    compare_output(r'\ifhbox12 bye\else text\fi\ifhbox16 one\else two\fi')

def testIfVBox():
    compare_output(r'\ifvbox12 bye\else text\fi\ifvbox16 one\else two\fi')

# This is defined to be unconditionally false
@pytest.mark.xfail
def testIfEOF():
    compare_output(r'\ifeof12 bye\else text\fi\ifeof15 one\else two\fi')

def testIfTrue():
    compare_output(r'\iftrue bye\else text\fi\iftrue one\else two\fi')

def testIfFalse():
    compare_output(r'\iffalse bye\else text\fi\iffalse one\else two\fi')

def testIfCase():
    compare_output(r'\ifcase 2 bye\or text\or one\else two\fi')

def testNestedIf():
    compare_output(r'\ifnum 2 < 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi foo')

def testNestedIf2():
    compare_output(r'\ifnum 2 > 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi foo')


def testNewIfIf():
    compare_output(r'before  \iftrue always \newif \iffoobar up \else down \fi then \iffoobar one \else two \fi allend')

def testUnterminatedIf(monkeypatch):
    mock_logger = Mock()
    monkeypatch.setattr('plasTeX.TeX.log.warning', mock_logger)
    TeX().input(r'\if one \else two ').parse()
    mock_logger.assert_called_once_with(r'\end occurred when \if was incomplete')

def test_ifdefined_ifcsname():
    t = TeX()
    t.input(r"""
    \ifdefined\mathbbm Yes Mathbbm \else No mathbbm\fi

    \ifcsname mathbbm\endcsname Yes Mathbbm \else No mathbbm\fi

    \newcommand\mathbbm[1]{{\mathbb{#1}}}

    \ifdefined\mathbbm Yes Mathbbm \else No mathbbm\fi

    \ifcsname mathbbm\endcsname Yes Mathbbm \else No mathbbm\fi
    """)
    assert t.parse().textContent == 'No mathbbmNo mathbbm Yes Mathbbm Yes Mathbbm '
