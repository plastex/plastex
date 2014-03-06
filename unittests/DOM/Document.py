#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class DocumentTest(TestCase):

    def testCreateElement(self):
        doc = Document()
        node = doc.createAttribute('node')
        assert isinstance(node, Node)
        assert node.nodeName == 'node'

    def testCreateDocumentFragment(self):
        doc = Document()
        node = doc.createDocumentFragment()
        assert isinstance(node, Node)
        assert len(node) == 0

    def testCreateTextNode(self):
        doc = Document()
        node = doc.createTextNode('foo')
        assert isinstance(node, Text)
        assert node == 'foo'
    
    def testCreateComment(self):
        doc = Document()
        node = doc.createComment('foo')
        assert isinstance(node, Comment)
        assert node == 'foo'

    def testCreateCDATASection(self):
        doc = Document()
        node = doc.createCDATASection('foo')
        assert isinstance(node, CDATASection)
        assert node == 'foo'

    def testCreateProcessingInstruction(self):
        pass
    
    def testAttribute(self):
        doc = Document()
        node = doc.createAttribute('foo')
        assert isinstance(node, Attr)
        assert node.nodeName == 'foo'

    def testEntityReference(self):
        pass
    
    def testGetElementsByTagName(self):
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        two2 = doc.createElement('two')
        three = doc.createElement('three')
        four = doc.createElement('four')
        five = doc.createElement('five')

        one.extend([two, three, four])
        four.extend([five, two2])
        doc.append(one)

        elems = doc.getElementsByTagName('two')
        assert len(elems) == 2
        assert elems[0] is two
        assert elems[1] is two2

        elems = doc.getElementsByTagName('three')
        assert len(elems) == 1
        assert elems[0] is three

    def testImportNode(self):
        doc = Document()
        doc2 = Document()
        two = doc2.createElement('two')
        three = doc.importNode(two)
        assert three.ownerDocument is doc
        assert two is not three

    def testAdoptNode(self):
        doc = Document()
        doc2 = Document()
        two = doc2.createElement('two')
        doc2.append(two)
        doc.adoptNode(two)
        assert len(doc) == 1
        assert len(doc2) == 0
        assert doc[0] is two

    def testNormalizeDocument(self):
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        text1 = doc.createTextNode('text1')
        text2 = doc.createTextNode('text2')
        text3 = doc.createTextNode('text3')

        doc.append(one)
        one.append(text1)
        one.append(two)
        two.extend([text2, text3])

        doc.normalizeDocument()

        elems = doc.getElementsByTagName('two')[0]
        assert len(elems) == 1, '%s != %s' % (len(elems), 1)
        assert elems.textContent == 'text2text3'

if __name__ == '__main__':
    unittest.main()

