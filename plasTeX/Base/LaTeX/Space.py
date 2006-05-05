#!/usr/bin/env python

"""
C.13.2 Space (p216)

"""

from plasTeX import Command, Environment, DimenCommand
from plasTeX.Logging import getLogger

class hspace(Command):
    args = '* len:dimen'

class vspace(Command):
    args = '* len:dimen'

class phantom(Command):
    args = 'text:str'

class bigskip(Command):
    pass

class medskip(Command):
    pass

class smallskip(Command):
    pass

class bigskipamount(DimenCommand):
    value = DimenCommand.new('24pt')

class medskipamount(DimenCommand):
    value = DimenCommand.new('12pt')

class smallskip(DimenCommand):
    value = DimenCommand.new('6pt')

class addvspace(Command):
    args = 'len:dimen'

class hfill(Command):
    pass

class vfill(Command):
    pass
