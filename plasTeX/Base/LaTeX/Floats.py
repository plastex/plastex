#!/usr/bin/env python

"""
C.9 Figures and Other Floating Bodies (p196)

"""

from plasTeX import Command, Environment, StringCommand, Counter, TheCounter
from plasTeX import Glue, glue, Dimen, dimen
from plasTeX.Logging import getLogger

class Caption(Command):
    args = '[ toc ] title'

#
# C.9.1 Figures and Tables
#

Counter('figure','chapter')
Counter('table','chapter')

class thefigure(TheCounter):
    format = '%(thechapter)s.%(figure)s'

class thetable(TheCounter):
    format = '%(thechapter)s.%(table)s'

class figure(Environment):
    args = 'loc:str'

    class caption(Caption):
        counter = 'figure'

class FigureStar(figure):
    macroName = 'figure*'

class table(Environment):
    args = 'loc:str'

    class caption(Caption):
        counter = 'table'

class TableStar(table):
    macroName = 'table*'

class suppressfloats(Command):
    pass

# Counters

Counter('topnumber')
Counter('bottomnumber')
Counter('totalnumber')
Counter('dbltopnumber')

class topfraction(StringCommand):
    value = '0.25'

class bottomfraction(StringCommand):
    value = '0.25'

class textfraction(StringCommand):
    value = '0.25'

class floatpagefraction(StringCommand):
    value = '0.25'

class dbltopfraction(StringCommand):
    value = '0.25'

class dblfloatpagefraction(StringCommand):
    value = '0.25'

class floatsep(Glue):
    value = glue(0)

class textfloatsep(Glue):
    value = glue(0)

class intextsep(Glue):
    value = glue(0)

class dblfloatsep(Glue):
    value = glue(0)

class dbltextfloatsep(Glue):
    value = glue(0)


#
# C.9.2 Marginal Notes
#

class marginpar(Command):
    args = '[ left ] right'

class reversemarginpar(Command):
    pass

class normalmarginpar(Command):
    pass

# Style Parameters

class marginparwidth(Dimen):
    value = dimen(0)

class marginparsep(Dimen):
    value = dimen(0)

class marginparpush(Dimen):
    value = dimen(0)
