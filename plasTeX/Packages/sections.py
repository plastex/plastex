#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment, TeXFragment, DOCUMENT

class _Section:
    """ Section utility methods """

    def subsections(self):
        """ Get a list of all subsections """
        return [x for x in self if x.section]

    def sectioncontent(self):
        """ Get all content that doesn't belong to subsections """
        content = []
        for obj in self:
            if not obj.section:
                content.append(obj)
        return TeXFragment(content)

    def sectionpath(self):
        """ Get the parentage of the current section """
        sections = [self]
        obj = self.parentNode
        while obj: 
            sections.append(obj)
            obj = obj.parentNode
        sections.reverse()
        return sections

class document(Environment, _Section):
    level = DOCUMENT

    def toXML(self):
        return '<?xml version="1.0"?>\n%s' % Environment.toXML(self)

class chapter(Command, _Section):
    section = True
    level = 0
    args = '* [ toc ] title'
    autoclose = True

class section(chapter):
    level = 1

class subsection(section):
    level = 2

class subsubsection(section):
    level = 3

class paragraph(section):
    level = 4

class subparagraph(section):
    level = 5

class subsubparagraph(section):
    level = 6

