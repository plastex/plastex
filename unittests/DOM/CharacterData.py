#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class CharacterDataTest(TestCase):

    def testNodeValue(self):
        doc = Document()
        one = doc.createTextNode('one')
        assert one.nodeValue == 'one'

    def testCloneNode(self):
        doc = Document()
        one = doc.createTextNode('one')
        clone = one.cloneNode()
        assert one == clone 

    def testData(self):
        doc = Document()
        one = doc.createTextNode('one')
        assert one.data == 'one' 
    
    def testLength(self):
        doc = Document()
        one = doc.createTextNode('one')
        assert one.length == 3
        
    def testTextContent(self):
        doc = Document()
        one = doc.createTextNode('one')
        assert one.textContent == 'one'
        
    def testIsSameNode(self):
        doc = Document()
        one = doc.createTextNode('one')
        two = doc.createTextNode('one')
        assert one.isSameNode(one)
        assert not one.isSameNode(two)

    def testIsEqualNode(self):
        doc = Document()
        one = doc.createTextNode('one')
        two = doc.createTextNode('one')
        three = doc.createTextNode('three')
        assert one.isEqualNode(one)
        assert one.isEqualNode(two)
        assert not one.isEqualNode(three)
        

if __name__ == '__main__':
    unittest.main()

