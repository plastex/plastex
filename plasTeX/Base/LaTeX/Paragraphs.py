#!/usr/bin/env python

"""
C.3.2 Making Paragraphs (p171)

"""

from plasTeX.Tokenizer import Other
from plasTeX import Command, Environment, StringCommand
from plasTeX import Dimen, dimen
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

class textwidth(Dimen):
    value = dimen('6.5in')

class columnwidth(Dimen):
    value = dimen('6.5in')

class linewidth(Dimen):
    value = dimen('6.5in')

class parindent(Dimen):
    value = dimen(0)

class baselineskip(Dimen):
    value = dimen('12pt')

class baselinestretch(StringCommand):
    value = '1'

class parskip(Dimen):
    value = dimen(0)
