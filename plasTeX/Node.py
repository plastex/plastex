#!/usr/bin/env python

import sys

class Node(object):

    # LaTeX document hierarchy
    DOCUMENT_LEVEL = -sys.maxint
    VOLUME_LEVEL = -2
    PART_LEVEL = -1
    CHAPTER_LEVEL = 0
    SECTION_LEVEL = 1
    SUBSECTION_LEVEL = 2
    SUBSUBSECTION_LEVEL = 3
    PARAGRAPH_LEVEL = 4
    SUBPARAGRAPH_LEVEL = 5
    SUBSUBPARAGRAPH_LEVEL = 6
    PAR_LEVEL = 10
    ENVIRONMENT_LEVEL = 20
    CHARACTER_LEVEL = COMMAND_LEVEL = 100

    level = CHARACTER_LEVEL    # Document hierarchy level of the node

    # DOM node types
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11
    NOTATION_NODE = 12

    nodeType = None

    # Relative document positions
    DOCUMENT_POSITION_DISCONNECTED = 0x01
    DOCUMENT_POSITION_PRECEDING = 0x02
    DOCUMENT_POSITION_FOLLOWING = 0x04
    DOCUMENT_POSITION_CONTAINS = 0x08
    DOCUMENT_POSITION_CONTAINED_BY = 0x10
    DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC = 0x20

    ownerDocument = None

    previousSibling = None
    nextSibling = None
    parentNode = None
    nodeName = None
    attributes = None
    childNodes = None

    contextDepth = 0   # TeX context level of this node (used during digest)

    def digest(self, tokens):
        return

    def nodeValue(self):
        return self
    nodeValue = property(nodeValue)

    def firstChild(self):
        if self.childNodes:
            return self.childNodes[0]
    firstChild = property(firstChild)

    def lastChild(self):
        if self.childNodes:
            return self.childNodes[-1]
    lastChild = property(lastChild)

    def hasChildNodes(self):
        return not(not(self.childNodes))
    hasChildNodes = property(hasChildNodes)

    def hasAttributes(self):
        return not(not(self.attributes))
    hasAttributes = property(hasAttributes)

    def isSameNode(self, other):
        return self is other

    def isEqualNode(self, other):
        return self == other

    def previousSibling(self):
        """ 
        Return the previous sibling 
    
        NOTE: This is fairly inefficient.  The reason that it has 
        to be done this way is because most nodes are a subclass of
        `unicode` which is an immutable object.  This means that 
        we can't have two references to the same node object (i.e.
        `previousSibling` and `nextSibling` can't be variables).
    
        """ 
        if not self.parentNode:
            return None
        previous = None
        for i, item in enumerate(self.parentNode):
            if item is self:
                return previous
            previous = item
        return None

    previousSibling = property(previousSibling)
    
    def nextSibling(self):
        """ 
        Return the next sibling 
    
        NOTE: This is fairly inefficient.  The reason that it has 
        to be done this way is because most nodes are a subclass of
        `unicode` which is an immutable object.  This means that 
        we can't have two references to the same node object (i.e.
        `previousSibling` and `nextSibling` can't be variables).
    
        """ 
        if not self.parentNode:
            return None
        next = False
        for i, item in enumerate(self.parentNode):
            if next:
                return item
            if item is self:
                next = True
        return None

    nextSibling = property(nextSibling)

    def compareDocumentPosition(self, other):
        """
        Compare the position of the current node to `other`
    
        Required Arguments:
        other -- the node to compare our position against
    
        Returns:
        DOCUMENT_POSITION_DISCONNECTED -- nodes are disconnected
        DOCUMENT_POSITION_PRECEDING -- `other` precedes this node
        DOCUMENT_POSITION_FOLLOWING -- `other` follows this node
        DOCUMENT_POSITION_CONTAINS -- `other` contains this node
        DOCUMENT_POSITION_CONTAINED_BY -- `other` is contained by this node
        DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC -- unknown
    
        """
        if self.ownerDocument is not other.ownerDocument:
            return Node.DOCUMENT_POSITION_DISCONNECTED
    
        if self.previousSibling is other:
            return Node.DOCUMENT_POSITION_PRECEDING
    
        if self.nextSibling is other:
            return Node.DOCUMENT_POSITION_FOLLOWING
    
        if self is other:
            return Node.DOCUMENT_IMPLEMENTATION_SPECIFIC
    
        sparents = []
        parent = self
        while parent is not None:
            if parent is other:
                return Node.DOCUMENT_POSITION_CONTAINS
            sparents.append(parent)
            parent = parent.parentNode
            
        oparents = []
        parent = other
        while parent is not None:
            if parent is self:
                return Node.DOCUMENT_POSITION_CONTAINED_BY
            oparents.append(parent)
            parent = parent.parentNode
    
        sparents.reverse()
        oparents.reverse()
    
        for i, sparent in enumerate(sparents):
            for j, oparent in enumerate(oparents):
                if sparent is oparent:
                    s = sparents[i+1]
                    o = oparents[j+1]
                    for item in sparent:
                       if item is s:
                           return Node.DOCUMENT_POSITION_FOLLOWING
                       if item is o:
                           return Node.DOCUMENT_POSITION_PRECEDING
    
        return Node.DOCUMENT_POSITION_DISCONNECTED
