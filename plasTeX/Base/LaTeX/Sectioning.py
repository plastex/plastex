#!/usr/bin/env python

"""
C.4 Sectioning and Table of Contents (p174)

"""

from plasTeX import Command, Environment, Counter, TheCounter
from plasTeX.Logging import getLogger

#
# C.4.1 Sectioning Commands
#

class StartSection(Command):
    args = '* [ toc ] title'

    def digest(self, tokens):
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.level <= self.level:
                tokens.push(item)
                break
            if item.nodeType == Command.ELEMENT_NODE:
                item.digest(tokens)
            self.appendChild(item)

Counter('part','volume')
Counter('chapter','part')
Counter('section','chapter')
Counter('subsection','section')
Counter('subsubsection','subsection')
Counter('paragraph','subsubsection')
Counter('subparagraph','paragraph')
Counter('subsubparagraph','subparagraph')

class thepart(TheCounter): 
    format = '%(part)s'

class thechapter(TheCounter): 
    format = '%(chapter)s'

class thesection(TheCounter): 
    format = '%(section)s'

class thesubsection(TheCounter): 
    format = '%(thesection)s.%(subsection)s'

class thesubsubsection(TheCounter): 
    format = '%(thesubsection)s.%(subsubsection)s'

class theparagraph(TheCounter):
    format = '%(thesubsubsection)s.%(paragraph)s'

class thesubparagraph(TheCounter):
    format = '%(theparagraph)s.%(subparagraph)s'

class thesubsubparagraph(TheCounter):
    format = '%(thesubparagraph)s.%(subsubparagraph)s'
    
class part(StartSection):
    level = Command.PART_LEVEL
    counter = 'part'

class chapter(StartSection):
    level = Command.CHAPTER_LEVEL
    counter = 'chapter'

class section(StartSection):
    level = Command.SECTION_LEVEL
    counter = 'section'

class subsection(StartSection):
    level = Command.SUBSECTION_LEVEL
    counter = 'subsection'

class subsubsection(StartSection):
    level = Command.SUBSUBSECTION_LEVEL
    counter = 'subsubsection'

class paragraph(StartSection):
    level = Command.PARAGRAPH_LEVEL
    counter = 'paragraph'

class subparagraph(StartSection):
    level = Command.SUBPARAGRAPH_LEVEL
    counter = 'subparagraph'

class subsubparagraph(StartSection):
    level = Command.SUBSUBPARAGRAPH_LEVEL
    counter = 'subsubparagraph'

#
# C.4.2 The Appendix
#

class appendix(Command):
    pass

#
# C.4.3 Table of Contents
#

class tableofcontents(Command):
    pass

class listoffigures(Command):
    pass

class listoftables(Command):
    pass

class addcontentsline(Command):
    args = 'file:str level:str text'

class addtocontents(Command):
    args = 'file:str text'

#
# C.4.4 Style Parameters
#

Counter('secnumdepth')
Counter('tocdepth')

