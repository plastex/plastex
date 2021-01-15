import unittest
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro

from helpers.utils import compare_output

import pytest

class TestIfs(TestCase):

    def testTrue(self):
        compare_output(r'\newif\iffoo\footrue\iffoo hi\else bye\fi')

    def testFalse(self):
        compare_output(r'\newif\iffoo\foofalse\iffoo hi\else bye\fi')

    def testIf(self):
        compare_output(r'\if*! bye\else text\fi\if** one\else two\fi')

    def testIfNum(self):
        compare_output(r'\ifnum 5 < 2 bye\else text\fi\ifnum 2 = 2 one\else two\fi')

    def testIfDim(self):
        compare_output(r'\ifdim -5 pt > 2in bye\else text\fi\ifdim 2mm = 2 mm one\else two\fi')

    def testIfOdd(self):
        compare_output(r'\ifodd 2 bye\else text\fi\ifodd 3 one\else two\fi')

    # This is not implemented correctly; it is unconditionally false
    @pytest.mark.xfail
    def testIfVMode(self):
        compare_output(r'\ifvmode bye\else text\fi\ifvmode one\else two\fi')

    # This is not implemented correctly; it is unconditionally true
    @pytest.mark.xfail
    def testIfHMode(self):
        compare_output(r'\ifhmode bye\else text\fi\ifhmode one\else two\fi')

    def testIfMMode(self):
        compare_output(r'\ifmmode bye\else text\fi\ifmmode one\else two\fi')

    def testIfInner(self):
        compare_output(r'\ifinner bye\else text\fi\ifinner one\else two\fi')

    def testIfCat(self):
        compare_output(r'\ifcat!a bye\else text\fi\ifcat!( one\else two\fi')

    def testIfX(self):
        compare_output(r'\ifx!!bye\else text\fi\ifx!( one\else two\fi')

    # This is defined to be unconditionally false
    @pytest.mark.xfail
    def testIfVoid(self):
        compare_output(r'\ifvoid12 bye\else text\fi\ifvoid16 one\else two\fi')

    def testIfHBox(self):
        compare_output(r'\ifhbox12 bye\else text\fi\ifhbox16 one\else two\fi')

    def testIfVBox(self):
        compare_output(r'\ifvbox12 bye\else text\fi\ifvbox16 one\else two\fi')

    # This is defined to be unconditionally false
    @pytest.mark.xfail
    def testIfEOF(self):
        compare_output(r'\ifeof12 bye\else text\fi\ifeof15 one\else two\fi')

    def testIfTrue(self):
        compare_output(r'\iftrue bye\else text\fi\iftrue one\else two\fi')

    def testIfFalse(self):
        compare_output(r'\iffalse bye\else text\fi\iffalse one\else two\fi')

    def testIfCase(self):
        compare_output(r'\ifcase 2 bye\or text\or one\else two\fi')

    def testNestedIf(self):
        compare_output(r'\ifnum 2 < 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi foo')

    def testNestedIf2(self):
        compare_output(r'\ifnum 2 > 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi foo')

    # TODO This works if the standard Python logging is used, see in TeX.py
    @pytest.mark.xfail
    def testUnterminatedIf(self):
        with self.assertLogs(level='WARNING') as cm:
            tex = r'\if one \else two '
            plastex_out = TeX().input(tex).parse().textContent.strip()
        expected_warning = 'WARNING:root:\\end occurred when \\if was incomplete'
        assert(expected_warning in cm.output), (" %r not in %r " % (expected_warning, cm.output))

if __name__ == '__main__':
    unittest.main()

