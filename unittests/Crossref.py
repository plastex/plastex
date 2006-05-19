#!/usr/bin/env python

import unittest, re
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro


class Labels(TestCase):

    def testLabel(self):
        s = TeX()
        s.input(r'\section{hi\label{one}} text \section{bye\label{two}}')
        output = s.parse()
        one = output[0]
        two = output[-1]
        assert one.id == 'one', one.id
        assert two.id == 'two', two.id

    def testLabelStar(self):
        s = TeX()
        s.input(r'\section{hi} text \section*{bye\label{two}}')
        output = s.parse()
        one = output[0]
        two = output[-1]
        assert one.id == 'two', one.id
        assert two.id != 'two', two.id


if __name__ == '__main__':
    unittest.main()

