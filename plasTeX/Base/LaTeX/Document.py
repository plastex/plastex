#!/usr/bin/env python

"""
C.2 The Structure of the Document (p170)

"""

from plasTeX import Command, Environment
from Sectioning import SectionUtils

class document(Environment, SectionUtils):
    level = Environment.DOCUMENT_LEVEL

    def digest(self, tokens):
        Environment.digest(self, tokens)
        self.paragraphs()
        if not self.ownerDocument:
            return
        for key, value in self.ownerDocument.userdata.items():
            self.attributes[key] = value

class AtEndDocument(Command):
    args = 'commands:nox'

class AtBeginDocument(Command):
    args = 'commands:nox'
