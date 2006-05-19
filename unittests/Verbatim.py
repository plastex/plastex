#!/usr/bin/env python

import unittest, re
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro

class Verbatim(TestCase):

    def testVerbatim(self):
        intext = 'line one\nline    two'
        input = 'hi \\begin{verbatim}\n%s\n\\end{verbatim} bye' % intext
        s = TeX()
        s.input(input)
        output = s.parse()
        output.normalize()
        text = ''.join(output.childNodes[1].childNodes).strip()
        assert intext == text, '"%s" != "%s"' % (intext, text)

    def testVerb(self):
        intext = r' verbatim \tt text '
        input = r'hi \verb+%s+ bye' % intext
        s = TeX()
        s.input(input)
        output = s.parse()
        output.normalize()
        text = ''.join(output.childNodes[1].childNodes)
        assert intext == text, '"%s" != "%s"' % (intext, text)

    def testVerbStar(self):
        intext = r' verbatim \tt text '
        input = r'hi \verb*+%s+ bye' % intext
        s = TeX()
        s.input(input)
        output = s.parse()
        output.normalize()
        text = ''.join(output.childNodes[1].childNodes)
        assert intext == text, '"%s" != "%s"' % (intext, text)


if __name__ == '__main__':
    unittest.main()

