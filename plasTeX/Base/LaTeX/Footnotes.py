#!/usr/bin/env python

"""
C.3.3 Footnotes (p172)

"""

from plasTeX import Dimen, dimen
from plasTeX import Command, Environment
from plasTeX.Logging import getLogger


class footnote(Command):
    args = '[ num:int ] self'

class footnotemark(Command):
    args = '[ num:int ]'

class footnotetext(Command):
    args = '[ num:int ] self'


#
# Style Parameters
#

class footnotesep(Dimen):
    value = dimen(0)

class footnoterule(Command):
    pass
