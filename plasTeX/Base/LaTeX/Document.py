#!/usr/bin/env python

"""
C.2 The Structure of the Document (p170)

"""

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Sectioning import SectionUtils

class document(Environment, SectionUtils):
    level = Environment.DOCUMENT_LEVEL

    @property
    def title(self):
        return self.ownerDocument.userdata.get('title','')

    @title.setter
    def title(self, value):
        self.ownerDocument.userdata["title"] = value

    def invoke(self, tex):
        res = Environment.invoke(self, tex)

        # Set initial counter values
        if 'counters' in self.config:
            counters = self.config['counters']
            for name in list(counters.keys()):
                if name.startswith(';'):
                    continue
                try:
                    self.ownerDocument.context.counters[name].setcounter(counters[name]-1)
                except TypeError:
                    self.ownerDocument.context.counters[name].setcounter(int(counters[name])-1)

        return res
 
    @property
    def index(self):
        idx = self.getElementsByTagName(['theindex','printindex'])
        if idx:
            return idx[0]
        return []

class AtEndDocument(Command):
    args = 'commands:nox'

class AtBeginDocument(Command):
    args = 'commands:nox'
