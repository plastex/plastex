#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class ElementTest(TestCase):

    def testTagName(self):
        doc = Document()
        one = doc.createElement('one')
        assert one.nodeName == 'one'
        assert one.tagName == 'one'

    def testSetGetRemoveAttribute(self):
        doc = Document()
        one = doc.createElement('one')
        one.setAttribute('foo', 'bar')
        assert one.attributes.keys() == ['foo']
        assert one.getAttribute('foo') == 'bar'
        assert one.getAttribute('aoeu') is None
        assert one.removeAttribute('aoeu') is None
        assert one.removeAttribute('foo') is None
        assert one.attributes.keys() == []

    def testHasAttribute(self):
        doc = Document()
        one = doc.createElement('one')
        one.setAttribute('foo', 'bar')
        assert one.hasAttribute('foo')
        assert not one.hasAttribute('aoeu')

    def testGetElementsByTagName(self):
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        twoClone = two.cloneNode()
        three = doc.createElement('three')
        four = doc.createElement('four')

        one.extend([two, three])
        three.extend([four, twoClone])

        elems = one.getElementsByTagName('two')
        assert len(elems) == 2, elems
        assert elems[0] is two
        assert elems[1] is twoClone

        elems = one.getElementsByTagName('four')
        assert len(elems) == 1
        assert elems[0] is four


if __name__ == '__main__':
    unittest.main()

