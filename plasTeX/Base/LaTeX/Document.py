#!/usr/bin/env python

"""
C.2 The Structure of the Document (p170)

"""

from plasTeX import Command, Environment

class document(Environment):
    level = Environment.DOCUMENT_LEVEL

    def digest(self, tex):
        Environment.digest(self, tex)
        self.paragraphs()
