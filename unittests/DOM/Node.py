#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class Construction(TestCase):

    def _checkPositions(self, node):
        """ Check the postions of all contained nodes """ 

        maxidx = len(node) - 1

        # Check firstChild and lastChild
        if node:
            assert node.firstChild is node[0], 'firstChild is incorrect'
            assert node.lastChild is node[maxidx], 'lastChild is incorrect'

        # Check nextSibling
        for i, item in enumerate(node):
            if i == maxidx:
                assert item.nextSibling is None, \
                       'nextSibling in position %s should be None' % i
            else:
                assert item.nextSibling is node[i+1], \
                       'nextSibling in position %s is incorrect (%s)' % \
                       (i, item.nextSibling)

        # Check previousSibling
        for i, item in enumerate(node):
            if i == 0:
                assert item.previousSibling is None, \
                       'previousSibling in position %s should be None' % i
            else:
                assert item.previousSibling is node[i-1], \
                       'previousSibling in position %s is incorrect (%s)' % \
                       (i, item.previousSibling)

        # Check parentNode
        for i, item in enumerate(node):
            assert item.parentNode is node, \
                   'parentNode in position %s is incorrect' % i

        # Check ownerDocument
        for i, item in enumerate(node):
            assert item.ownerDocument is node.ownerDocument, \
                   'ownerDocument in position %s is incorrect' % i

        # Check attributes
        if node.attributes:
            for key, value in node.attributes.items():
                if isinstance(value, Node):
                    assert value.parentNode is node, \
                           'parentNode is incorrect (%s)' % value.parentNode
                    self._checkPositions(value)

                elif isinstance(value, list):
                    for item in value:
                        assert item.parentNode is node, \
                               'parentNode is incorrect (%s)' % item.parentNode
                        self._checkPositions(item)

                elif isinstance(value, dict):
                    for item in value.values():
                        assert item.parentNode is node, \
                               'parentNode is incorrect (%s)' % item.parentNode
                        self._checkPositions(item)

    def testConstructor(self):
        """ Passing list of nodes to constructor """
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createElement('three')
        node = Node([one,two,three])
        expected = [one,two,three]
        for i, item in enumerate(node):
            assert item is expected[i], '"%s" != "%s"' % (item, expected[i])
        self._checkPositions(node)

    def testInsert(self):
        """ Insert into empty node """
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createElement('three')
        node = Node()
        node.insert(0, one)
        node.insert(1, two)
        node.insert(2, three)
        expected = [one,two,three]
        for i, item in enumerate(node):
            assert item is expected[i], '"%s" != "%s"' % (item, expected[i])
        self._checkPositions(node)

    def testInsert2(self):
        """ Insert into populated node """
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createElement('three')
        node = Node([one,two,three])
        i0 = doc.createElement('i0')
        i3 = doc.createTextNode('i3')
        node.insert(0, i0)
        node.insert(3, i3)
        expected = [i0,one,two,i3,three]
        for i, item in enumerate(node):
            assert item is expected[i], '"%s" != "%s"' % (item, expected[i])
        self._checkPositions(node)

    def testAttributes(self):
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createTextNode('three')
        node = Node()
        node.attributes['one'] = one
        one.attributes['two'] = two
        two.attributes['three'] = three 
        self._checkPositions(node)

if __name__ == '__main__':
    unittest.main()

