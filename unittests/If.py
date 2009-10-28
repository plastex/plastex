#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro


class TestIfs(TestCase):

    def testTrue(self):
        s = TeX()
        s.input(r'\newif\iffoo\footrue\iffoo hi\else bye\fi')
        output = [x for x in s]
        tail = ''.join(output[-2:]).strip()
        assert tail == 'hi', '"%s"' % tail

    def testFalse(self):
        s = TeX()
        s.input(r'\newif\iffoo\foofalse\iffoo hi\else bye\fi')
        output = [x for x in s]
        tail = ''.join(output[-3:]).strip()
        assert tail == 'bye', '"%s"' % tail

    def testIf(self):
        s = TeX()
        s.input(r'\if*! bye\else text\fi\if** one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfNum(self):
        s = TeX()
        s.input(r'\ifnum 5 < 2 bye\else text\fi\ifnum 2 = 2 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfDim(self):
        s = TeX()
        s.input(r'\ifdim -5 pt > 2in bye\else text\fi\ifdim 2mm = 2 mm one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'textone'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfOdd(self):
        s = TeX()
        s.input(r'\ifodd 2 bye\else text\fi\ifodd 3 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfEven(self):
        s = TeX()
        s.input(r'\ifeven 7 bye\else text\fi\ifeven 100 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfVMode(self):
        s = TeX()
        s.input(r'\ifvmode bye\else text\fi\ifvmode one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'texttwo'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfHMode(self):
        s = TeX()
        s.input(r'\ifhmode bye\else text\fi\ifhmode one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'byeone'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfMMode(self):
        s = TeX()
        s.input(r'\ifmmode bye\else text\fi\ifmmode one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'texttwo'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfInner(self):
        s = TeX()
        s.input(r'\ifinner bye\else text\fi\ifinner one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'texttwo'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfCat(self):
        s = TeX()
        s.input(r'\ifcat!a bye\else text\fi\ifcat!( one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfX(self):
        s = TeX()
        s.input(r'\ifx!!bye\else text\fi\ifx!( one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'bye two'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfVoid(self):
        s = TeX()
        s.input(r'\ifvoid12 bye\else text\fi\ifvoid16 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text two'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfHBox(self):
        s = TeX()
        s.input(r'\ifhbox12 bye\else text\fi\ifhbox16 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text two'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfVBox(self):
        s = TeX()
        s.input(r'\ifvbox12 bye\else text\fi\ifvbox16 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'text two'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfEOF(self):
        s = TeX()
        s.input(r'\ifeof12 bye\else text\fi\ifeof16 one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'texttwo'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfTrue(self):
        s = TeX()
        s.input(r'\iftrue bye\else text\fi\iftrue one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'byeone'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfFalse(self):
        s = TeX()
        s.input(r'\iffalse bye\else text\fi\iffalse one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'texttwo'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testIfCase(self):
        s = TeX()
        s.input(r'\ifcase 2 bye\or text\or one\else two\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'one'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testNestedIf(self):
        s = TeX()
        s.input(r'\ifnum 2 < 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi')
        output = ''.join([x for x in s]).strip()
        expected = 'byetext hi'
        assert output == expected, '"%s" != "%s"' % (output, expected)

    def testNestedIf2(self):
        s = TeX()
        s.input(r'\ifnum 2 > 3 bye\iftrue text\ifcat() hi\fi\else one\fi\fi')
        output = [x for x in s]
        expected = [' ']
        assert output == expected, '"%s" != "%s"' % (output, expected)

if __name__ == '__main__':
    unittest.main()

