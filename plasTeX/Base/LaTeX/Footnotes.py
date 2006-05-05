#!/usr/bin/env python

"""
C.3.3 Footnotes (p172)

"""

from plasTeX import Command, Environment, DimenCommand
from plasTeX.Logging import getLogger


class footnote(Command):
    args = '[ num:int ] self'

    def digest(self, tokens):
        # Add the footnote to the document
        output = Command.digest(self, tokens)
        userdata = self.ownerDocument.userdata
        if 'footnotes' not in userdata:
            userdata['footnotes'] = []
        userdata['footnotes'].append(self)

class footnotemark(Command):
    args = '[ num:int ]'

    def digest(self, tokens):
        # Add the footnotemarks to the document
        output = Command.digest(self, tokens)
        userdata = self.ownerDocument.userdata
        if 'footnotemarks' not in userdata:
            userdata['footnotemarks'] = []
        userdata['footnotemarks'].append(self)

class footnotetext(footnote):
    args = '[ num:int ] self'


#
# Style Parameters
#

class footnotesep(DimenCommand):
    value = DimenCommand.new(0)

class footnoterule(Command):
    pass
