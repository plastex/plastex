#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.DOM import *

class NodeTest(TestCase):

    def _checkPositions(self, node):
        """ Check the postions of all contained nodes """ 
        if isinstance(node, CharacterData):
            return
            
        if not(isinstance(node, Node)):
            return 

        maxidx = len(node) - 1

        # Check firstChild and lastChild
        if node.childNodes:
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
                   'ownerDocument in position %s (%s) is incorrect: %s' % (i, item.ownerDocument, node.ownerDocument)

        # Check attributes
        if node.attributes:
            for key, value in node.attributes.items():
                if isinstance(value, Node):
                    assert value.parentNode is node, \
                           'parentNode is incorrect (%s)' % value.parentNode
                    self._checkPositions(value)

                elif isinstance(value, list):
                    for item in value:
                        assert getattr(item, 'parentNode', node) is node, \
                               'parentNode is incorrect (%s)' % item.parentNode
                        self._checkPositions(item)

                elif isinstance(value, dict):
                    for item in value.values():
                        assert getattr(item, 'parentNode', node) is node, \
                               'parentNode is incorrect (%s)' % item.parentNode
                        self._checkPositions(item)

    def testConstructor(self):
        """ Passing list of nodes to constructor """
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createElement('three')
        node = doc.createElement('top')
        node.extend([one,two,three])
        expected = [one,two,three]
        for i, item in enumerate(node):
            assert item is expected[i], '"%s" != "%s"' % (item, expected[i])
        self._checkPositions(node)

#   def testAttributes(self):
#       """ Set attributes on a node """
#       doc = Document()
#       one = doc.createElement('one')
#       two = doc.createElement('two')
#       three = doc.createTextNode('three')
#       four = ['hi','bye',Text('text node')]
#       node = Node()
#       node.attributes['one'] = one
#       one.attributes['two'] = two
#       two.attributes['three'] = three 
#       two.attributes['four'] = four 
#       self._checkPositions(node)

    def testFirstChild(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createElement('two')
        assert node.firstChild is None, '"%s" != None' % node.firstChild 
        node.append(one)
        assert node.firstChild is one, '"%s" != "%s"' % (node.firstChild, one)
        node.insert(0, two)
        assert node.firstChild is two, '"%s" != "%s"' % (node.firstChild, two)
        self._checkPositions(node)

    def testLastChild(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createElement('two')
        assert node.lastChild is None, '"%s" != None' % node.lastChild 
        node.append(one)
        assert node.lastChild is one, '"%s" != "%s"' % (node.lastChild, one)
        node.append(two)
        assert node.lastChild is two, '"%s" != "%s"' % (node.lastChild, two)
        self._checkPositions(node)

    def testChildNodes(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.append(three)
        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is two, '"%s" != "%s"' % (node[1], two)
        assert node[2] is three, '"%s" != "%s"' % (node[2], three)
        assert node.childNodes[0] is one, '"%s" != "%s"' % (node.childNodes[0], one)
        assert node.childNodes[1] is two, '"%s" != "%s"' % (node.childNodes[1], two)
        assert node.childNodes[2] is three, '"%s" != "%s"' % (node.childNodes[2], three)
        self._checkPositions(node)

    def testPreviousSibling(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.append(three)
        assert None is one.previousSibling, 'None != "%s"' % one.previousSibling
        assert one is two.previousSibling, '"%s" != "%s"' % (one, two.previousSibling)
        assert two is three.previousSibling, '"%s" != "%s"' % (two, three.previousSibling)

    def testNextSibling(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.append(three)
        assert two is one.nextSibling, '"%s" != "%s"' % (two, one.nextSibling)
        assert three is two.nextSibling, '"%s" != "%s"' % (three, two.nextSibling)
        assert None is three.nextSibling, 'None != "%s"' % three.nextSibling

    def testOwnerDocument(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.attributes['three'] = three
        a = Text('a')
        b = Text('b')
        node.attributes['four'] = {'a':a, 'b':1}
        node.attributes['five'] = [b, 1, 'c']
        assert node.ownerDocument is doc, '"%s" != "%s"' % (node.ownerDocument, doc)
        assert one.ownerDocument is doc, '"%s" != "%s"' % (one.ownerDocument, doc)
        assert two.ownerDocument is doc, '"%s" != "%s"' % (two.ownerDocument, doc)
        assert three.ownerDocument is doc, '"%s" != "%s"' % (three.ownerDocument, doc)
        assert a.ownerDocument is doc, '"%s" != "%s"' % (a.ownerDocument, doc)
        assert b.ownerDocument is doc, '"%s" != "%s"' % (b.ownerDocument, doc)
        self._checkPositions(node)
        

    def testCompareDocumentPosition(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        four = doc.createElement('four')
        node.append(one)
        node.append(two)
        node.append(three)
        three.append(four)
        five = doc.createElement('five')

        expected = Node.DOCUMENT_POSITION_FOLLOWING
        rc = one.compareDocumentPosition(four)
        assert rc == expected, '"%s" != "%s"' % (rc, expected)

        expected = Node.DOCUMENT_POSITION_PRECEDING
        rc = four.compareDocumentPosition(one)
        assert rc == expected, '"%s" != "%s"' % (rc, expected)

        expected = Node.DOCUMENT_POSITION_CONTAINED_BY
        rc = node.compareDocumentPosition(four)
        assert rc == expected, '"%s" != "%s"' % (rc, expected)

        expected = Node.DOCUMENT_POSITION_CONTAINS
        rc = four.compareDocumentPosition(node)
        assert rc == expected, '"%s" != "%s"' % (rc, expected)

        expected = Node.DOCUMENT_POSITION_DISCONNECTED
        rc = five.compareDocumentPosition(node)
        assert rc == expected, '"%s" != "%s"' % (rc, expected)

    def testInsertBefore(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.insertBefore(three, two)
        assert node[1] is three, '"%s" != "%s"' % (node[1], three)
        node.insertBefore(three, one)
        assert node[0] is three, '"%s" != "%s"' % (node[0], three)
        assert node[1] is one, '"%s" != "%s"' % (node[1], one)
        assert node[2] is two, '"%s" != "%s"' % (node[2], two)
        self._checkPositions(node)

    def testReplaceChild(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)
        node.replaceChild(three, two)
        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is three, '"%s" != "%s"' % (node[1], three)
        assert len(node) == 2, '%s != %s' % (len(node), 2)
        self._checkPositions(node)

    def testRemoveChild(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.append(one)
        node.append(two)

        res = node.removeChild(one)
        assert res is one, '"%s" != "%s"' % (res, one)
        assert len(node) == 1, '%s != %s' % (len(node), 1)
        assert node[0] is two, '"%s" != "%s"' % (node[0], two)
        self._checkPositions(node)

        res = node.removeChild(two)
        assert res is two, '"%s" != "%s"' % (res, two)
        assert len(node) == 0, '%s != %s' % (len(node), 0)

    def testPop(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.extend([one, two, three])

        res = node.pop()
        assert res is three, '"%s" != "%s"' % (res, three)
        assert len(node) == 2, '%s != %s' % (len(node), 2)
        self._checkPositions(node)

        res = node.pop(0)
        assert res is one, '"%s" != "%s"' % (res, one)
        assert len(node) == 1, '%s != %s' % (len(node), 1)
        self._checkPositions(node)

    def testAppendChild(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        node.appendChild(one)
        frag = doc.createDocumentFragment()
        frag.appendChild(two)
        frag.appendChild(three)
        node.appendChild(frag)

        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is two, '"%s" != "%s"' % (node[1], two)
        assert node[2] is three, '"%s" != "%s"' % (node[2], three)
        self._checkPositions(node)

    def testInsert(self):
        """ Insert into empty node """
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createElement('three')
        node = doc.createElement('top')
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
        node = doc.createElement('top')
        node.extend([one,two,three])
        i0 = doc.createElement('i0')
        i3 = doc.createTextNode('i3')
        node.insert(0, i0)
        node.insert(3, i3)
        expected = [i0,one,two,i3,three]
        for i, item in enumerate(node):
            assert item is expected[i], '"%s" != "%s"' % (item, expected[i])
        self._checkPositions(node)

    def testInsert3(self):
        """ Insert document fragment """
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        four = doc.createElement('four')
        node.appendChild(one)
        node.appendChild(two)
        frag = doc.createDocumentFragment()
        frag.appendChild(three)
        frag.appendChild(four)
        node.insert(1,frag)

        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is three, '"%s" != "%s"' % (node[1], three)
        assert node[2] is four, '"%s" != "%s"' % (node[2], four)
        assert node[3] is two, '"%s" != "%s"' % (node[3], two)
        self._checkPositions(node)
        
    def testSetItem(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        four = doc.createElement('four')
        five = doc.createElement('five')
        node.appendChild(one)
        node.appendChild(two)
        node.appendChild(three)

        node[1] = four
        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is four, '"%s" != "%s"' % (node[1], four)
        assert node[2] is three, '"%s" != "%s"' % (node[2], three)
        assert len(node) == 3, '%s != %s' % (len(node), 3)
        self._checkPositions(node)

        node[2] = five
        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is four, '"%s" != "%s"' % (node[1], four)
        assert node[2] is five, '"%s" != "%s"' % (node[2], five)
        assert len(node) == 3, '%s != %s' % (len(node), 3)
        self._checkPositions(node)

    def testExtend(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createElement('three')
        four = doc.createElement('four')
        five = doc.createElement('five')
        node.appendChild(one)

        node.extend([two, three])
        assert node[0] is one, '"%s" != "%s"' % (node[0], one)
        assert node[1] is two, '"%s" != "%s"' % (node[1], two)
        assert node[2] is three, '"%s" != "%s"' % (node[2], three)
        assert len(node) == 3, '%s != %s' % (len(node), 3)
        self._checkPositions(node)

        node += [four, five]
        assert node[3] is four, '"%s" != "%s"' % (node[3], four)
        assert node[4] is five, '"%s" != "%s"' % (node[4], five)
        assert len(node) == 5, '%s != %s' % (len(node), 5)
        self._checkPositions(node)

    def testAdd(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        node.appendChild(one)
        node.appendChild(two)

        node2 = doc.createElement('node2')
        three = doc.createElement('three')
        four = doc.createElement('four')
        node.appendChild(three)
        node.appendChild(four)

        res = node + node2
        assert isinstance(res, Node), '%s is not a Node' % res
        assert res[0] is one, '"%s" != "%s"' % (res[0], one)
        assert res[1] is two, '"%s" != "%s"' % (res[1], two)
        assert res[2] is three, '"%s" != "%s"' % (res[2], three)
        assert res[3] is four, '"%s" != "%s"' % (res[3], four)
        self._checkPositions(res)

    def testHasChildNodes(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')

        assert not node.hasChildNodes()

        node.appendChild(one)
        node.appendChild(two)

        assert node.hasChildNodes()

    def testCloneNode(self):
        doc = Document()
        one = doc.createElement('one')
        two = doc.createElement('two')
        three = doc.createTextNode('three')
        two.append(three)
        one.append(two)

        res = one.cloneNode(1)
        assert type(res) is type(one), '"%s" != "%s"' % (type(res), type(one))
        assert type(res[0]) is type(one[0])
        assert one == res
        assert one is not res
        assert one[0] is not res[0]

    def testNormalize(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createTextNode('two')
        three = doc.createTextNode('three')
        four = doc.createTextNode('four')
        node.extend([one,two,three,four])
        node.normalize()
        assert len(node) == 2, '"%s" != "%s"' % (len(node), 2)
        assert node[1] == 'twothreefour', '"%s" != "%s"' % (node[1], 'twothreefour')

    def testIsSupported(self):
        pass
   
    def testHasAttributes(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        assert not node.hasAttributes()

        node.attributes['one'] = one
        assert node.hasAttributes()

    def testTextContent(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createTextNode('one')
        two = doc.createElement('two')
        three = doc.createTextNode('three')
        four = doc.createTextNode('four')
        node.append(one)
        node.append(two)
        two.extend([three, four])

        res = node.textContent
        expected = 'onethreefour'
        assert res == expected, '"%s" != "%s"' % (res, expected)

    def testIsSameNode(self):
        doc = Document()
        node = doc.createElement('node')
        assert node.isSameNode(node)

        clone = node.cloneNode()
        assert not node.isSameNode(clone)

    def testLookupPrefix(self):
        pass

    def testIsDefaultNamespace(self):
        pass

    def testLookupNamespaceURI(self):
        pass

    def testIsEqualNode(self):
        doc = Document()
        node = doc.createElement('node')
        one = doc.createElement('one')
        two = doc.createElement('two')
        node.extend([one, two])
        node2 = node.cloneNode(deep=True)
        assert node.isEqualNode(node2)

    def testGetFeature(self):
        pass

    def testGetSetUserData(self):
        doc = Document()
        node = doc.createElement('node')
        node.setUserData('foo', 'bar')
        res = node.getUserData('foo')
        assert res == 'bar'


if __name__ == '__main__':
    unittest.main()

