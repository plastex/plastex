#!/usr/bin/env python

"""
C.4 Sectioning and Table of Contents (p174)

"""

from plasTeX import Command, Environment
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

#class secnumdepth(Counter):
#    pass

#class tocdepth(Counter):
#    pass


