#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class TextTest(TestCase):

    def testIsElementContentWhitespace(self):
        doc = Document()
        one = doc.createTextNode('one')
        two = doc.createTextNode(' \t \r')
        assert not one.isElementContentWhitespace
        assert two.isElementContentWhitespace

    def testWholeText(self):
        doc = Document()
        one = doc.createTextNode('one')
        two = doc.createTextNode('two')
        three = doc.createTextNode('three')
        node = doc.createElement('node')
        node.extend([one, two, three])
        assert one.wholeText == 'onetwothree'


if __name__ == '__main__':
    unittest.main()

