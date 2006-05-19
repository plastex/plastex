#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX import Macro
from plasTeX.TeX import *

class ActiveChars(TestCase):

    def testActive(self):
        t = TeX()
        t.input(r'\catcode`|=\active \def|#1{\bf#1} |{bold text}')
        output = t.parse()
        assert output[-1].nodeName == 'bf', output[-1].nodeName

    def testActive2(self):
        t = TeX()
        t.input(r'\catcode`|=\active\catcode`/=\active \def|#1{\textbf{#1}/} \def/{\textit{the end}} |{bold text}')
        output = t.parse()
        assert output[-2].nodeName == 'textbf', output[-2].nodeName
        assert output[-1].nodeName == 'textit', output[-1].nodeName

    def testActiveSource(self):
        t = TeX()
        t.input(r'~')
        t = t.parse()
        assert t.source.strip() == '~', t.source.strip()


if __name__ == '__main__':
    unittest.main()

