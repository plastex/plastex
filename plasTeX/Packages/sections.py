#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment, TeXFragment, DOCUMENT

class _Section:
    """ Section utility methods """

    def subsections(self):
        """ Get a list of all subsections """
        sections = []
        for obj in self:
            if obj.section:
                sections.append(obj)
        return TeXFragment(sections)

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

    def __init__(self, *args, **kwargs):
        Environment.__init__(self, *args, **kwargs)
        self.preamble = None

    def parse(self, tex):
        # Save the preamble for use later
        self.preamble = type(tex).persistent.getSource(0,self._source.start)
        return Environment.parse(self, tex)

    def digest(self, tokens):
        Environment.digest(self, tokens)
        self[:] = paragraphs(self, type(type(self).context['par']),
                             allow_single=True)
        return self

    def toXML(self):
        return '<?xml version="1.0"?>\n%s' % Environment.toXML(self)

class chapter(Command, _Section):
    section = True
    level = 0
    args = '* [ toc ] title'

    def digest(self, tokens):
        Command.digest(self, tokens)
        self[:] = paragraphs(self, type(type(self).context['par']),
                             allow_single=True)
        return self

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

