#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX.Tokenizer import CC_EXPANDED
from plasTeX import Command, Environment

class document(Environment):
    level = DOCUMENT
    def toXML(self):
        return '<?xml version="1.0"?>\n%s' % Environment.toXML(self)

class StartSection(Command):
    args = '* [ toc ] title'

    def digest(self, tokens):
        self.children = []
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.code == CC_EXPANDED:
                item.digest(tokens)
            if item.level <= self.level:
                tokens.push(item)
                break
            self.children.append(item)
    
class chapter(StartSection):
    level = CHAPTER

class section(StartSection):
    level = SECTION

class subsection(StartSection):
    level = SUBSECTION

class subsubsection(StartSection):
    level = SUBSUBSECTION 

class paragraph(StartSection):
    level = PARAGRAPH

class subparagraph(StartSection):
    level = SUBPARAGRAPH

class subsubparagraph(StartSection):
    level = SUBSUBPARAGRAPH

