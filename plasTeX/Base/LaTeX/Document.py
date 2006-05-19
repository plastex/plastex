#!/usr/bin/env python

"""
C.2 The Structure of the Document (p170)

"""

from plasTeX import Command, Environment
from Sectioning import SectionUtils

class document(Environment, SectionUtils):
    level = Environment.DOCUMENT_LEVEL

    def invoke(self, tex):
        res = Environment.invoke(self, tex)

        # Copy attributes from the document
        for attr in ['title']:
            if attr in self.ownerDocument.userdata:
                self.attributes[attr] = self.ownerDocument.userdata[attr]

        # Set initial counter values
        if self.config.has_key('counters'):
            counters = self.config['counters']
            for name in counters.keys():
                if name.startswith(';'):
                    continue
                self.ownerDocument.context.counters[name].setcounter(counters[name]-1)

        return res

class AtEndDocument(Command):
    args = 'commands:nox'

class AtBeginDocument(Command):
    args = 'commands:nox'
