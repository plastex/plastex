#!/usr/bin/env python

from Accents import *
from Alignment import *
from Arrays import *
from Bibliography import *
from Boxes import *
from Breaking import *
from Crossref import *
from Definitions import *
from Document import *
from Environments import *
from FontSelection import *
from Footnotes import *
from Files import *
from Floats import *
from Index import *
from Lengths import *
from Lists import *
from Math import *
from Numbering import *
from Packages import *
from Pictures import *
from Paragraphs import *
from Quotations import *
from Sectioning import *
from Sentences import *
from Space import *
from Tabbing import *
from Verbatim import *

from plasTeX import Command

class ifundefined_(Command):
    macroName = '@ifundefined'
    args = 'name:str true:nox false:nox'
    def invoke(self, tex):
        a = self.parse(tex)
        if tex.context.has_key(a['name']):
            tex.pushtokens(a['true'])
        else:
            tex.pushtokens(a['false'])
        return []

class vwritefile_(Command):
    macroName = '@vwritefile'
    args = 'file:nox content:nox'

class pagelabel(Command):
    args = 'label:nox content:nox'
