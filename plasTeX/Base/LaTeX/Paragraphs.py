#!/usr/bin/env python

"""
C.3.2 Making Paragraphs (p171)

"""

from plasTeX.Tokenizer import Other
from plasTeX import Command, Environment, DimenCommand
from plasTeX.Logging import getLogger

class noindent(Command):
    pass

class indent(Command):
    pass

# Defined in TeX
#class par(Command):
#    pass

#
# Style Parameters
#

class textwidth(DimenCommand):
    value = DimenCommand.new('6.5in')

class columnwidth(DimenCommand):
    value = DimenCommand.new('6.5in')

class linewidth(DimenCommand):
    value = DimenCommand.new('6.5in')

class parindent(DimenCommand):
    value = DimenCommand.new(0)

class baselineskip(DimenCommand):
    value = DimenCommand.new('12pt')

class baselinestretch(Command):
    str = '1'

class parskip(DimenCommand):
    value = DimenCommand.new(0)
