#!/usr/bin/env python

import unittest, re
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro

class InlineStyle(TestCase):

    def testNoStyle(self):
        input = '\\texttt{hi}'
        s = TeX()
        s.input(input)
        output = s.parse()
        node = output.childNodes[0]
        style = node.style.inline
        assert style is None

    def testEmptyStyle(self):
        input = '\\texttt{hi}'
        s = TeX()
        s.input(input)
        output = s.parse()
        node = output.childNodes[0]
        node.style['width'] = ''
        style = node.style.inline
        assert style is None

    def testOneStyle(self):
        input = '\\texttt{hi}'
        s = TeX()
        s.input(input)
        output = s.parse()
        node = output.childNodes[0]
        node.style['width'] = '100%'
        style = node.style.inline
        assert style == 'width:100%'

    def testTwoStyles(self):
        input = '\\texttt{hi}'
        s = TeX()
        s.input(input)
        output = s.parse()
        node = output.childNodes[0]
        node.style['width'] = '100%'
        node.style['height'] = '100%'
        style = node.style.inline
        assert style == 'width:100%; height:100%'

    def testEmptyStyleExcluded(self):
        input = '\\texttt{hi}'
        s = TeX()
        s.input(input)
        output = s.parse()
        node = output.childNodes[0]
        node.style['width'] = ''
        node.style['height'] = '100%'
        style = node.style.inline
        assert style == 'height:100%'

if __name__ == '__main__':
    unittest.main()

