#!/usr/bin/env python

"""
C.4 Sectioning and Table of Contents (p174)

"""

from plasTeX.Config import config
from plasTeX import Command, Environment, Counter, TheCounter, TeXFragment
from plasTeX.Logging import getLogger

#
# C.4.1 Sectioning Commands
#

class cachedproperty(object):
    def __init__(self, func):
        self._func = func
    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try: 
            return getattr(obj, '@%s' % self._func.func_name)
        except AttributeError:
            result = self._func(obj)
            setattr(obj, '@%s' % self._func.func_name, result)
            return result

class SectionUtils(object):
    """ General utilities for getting information about sections """

    def subsections(self):
        """
        Retrieve a list of all immediate subsections of this section

        """
        return [x for x in self if x.level < Command.ENDSECTIONS_LEVEL]
    subsections = cachedproperty(subsections)

    def allSections(self):
        """
        Retrieve a list of all sections within (and including) this one

        """
        sections = [self]
        for item in self.subsections:
            sections.extend(item.allSections)
        return sections
    allSections = cachedproperty(allSections)

    def documentSections(self):
        """
        Retrieve a list of all sections in the document

        """
        document = self
        while document.level is not Command.DOCUMENT_LEVEL:
            document = document.parentNode
            if document is None:
                return []
        return document.allSections
    documentSections = cachedproperty(documentSections)

    def navigation(self):
        """
        Return a dictionary containing a lot of navigation information
 
        See http://fantasai.tripod.com/qref/Appendix/LinkTypes/ltdef.html

        """
        sections = self.documentSections

        breadcrumbs = [self]
        parent = None
        if self.level > Command.DOCUMENT_LEVEL:
            item = parent = self.parentNode
            while item is not None:
                breadcrumbs.append(item)
                item = item.parentNode
                if item.level == Command.DOCUMENT_LEVEL:
                    breadcrumbs.append(item)
                    break
        breadcrumbs.reverse()

        top = sections[0]
        first = sections[0]
        last = sections[-1]
        prev = next = None
        breaknext = False
        for item in sections:
            if item is self:
                breaknext = True
                continue     
            if breaknext:
                next = item
                break
            prev = item

        nav = {}
        nav['home'] = top
        nav['start'] = top
        nav['begin'] = nav['first'] = first
        nav['end'] = nav['last'] = last
        nav['next'] = next
        nav['previous'] = nav['prev'] = prev
        nav['up'] = parent
        nav['top'] = nav['origin'] = top
        nav['parent'] = parent
        nav['child'] = self.subsections
        nav['sibling'] = None
        nav['chapter'] = None
        nav['section'] = None
        nav['subsection'] = None
        nav['appendix'] = None
        nav['glossary'] = None
        nav['bibliography'] = None
        nav['help'] = None
        nav['navigator'] = top
        nav['toc'] = nav['contents'] = top
        nav['index'] = None
        nav['search'] = None
        nav['bookmark'] = None
        nav['banner'] = None
        nav['copyright'] = None
        nav['trademark'] = None
        nav['disclaimer'] = None
        nav['publisher'] = None
        nav['editor'] = None
        nav['author'] = None
        nav['made'] = None
        nav['meta'] = None
        nav['script'] = None
        nav['stylesheet'] = None
        nav['alternate'] = None
        nav['translation'] = None

        # Additional related entries
        nav['shortcut icon'] = None
        nav['breadcrumbs'] = breadcrumbs

        return nav

    navigation = cachedproperty(navigation)

Counter('part','volume')
Counter('chapter','part')
Counter('section','chapter')
Counter('subsection','section')
Counter('subsubsection','subsection')
Counter('paragraph','subsubsection')
Counter('subparagraph','paragraph')
Counter('subsubparagraph','subparagraph')

class StartSection(Command, SectionUtils):
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
        self.paragraphs()

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

