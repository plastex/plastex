#!/usr/bin/env python

"""
C.10.1 The tabbing Environment (p201)

"""

from plasTeX import Command, Environment
from plasTeX import Dimen, dimen
from plasTeX.Logging import getLogger

class tabbing(Environment):

    class SetTabStop(Command):
        macroName = '='

    class JumpTabStop(Command):
        macroName = '>'

    class EndRow(Command):
        macroName = '\\\\'
   
    class kill(Command):
        pass

    class IncrementTab(Command):
        macroName = '+'

    class DecrementTab(Command):
        macroName = '-'

    class JumpBackTabStop(Command):
        macroName = '<' 

    class LeftMargin(Command):
        macroName = "'"

    class RightMargin(Command):
        macroName = '`'

    class pushtabs(Command):
        pass

    class poptabs(Command):
        pass

    class a(Command):
        args = 'accent'


# Style Parameters

class tabbingsep(Dimen):
    value = dimen(0)
