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

    parentNode = None
    ownerDocument = None
    previousSibling = None
    nextSibling = None


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

