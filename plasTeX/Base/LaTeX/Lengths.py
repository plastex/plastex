#!/usr/bin/env python

"""
C.13.1 Length (p215)

"""

from plasTeX import Command, Environment
from plasTeX import Dimen, dimen
from plasTeX.Logging import getLogger


class fill(Dimen):
    value = dimen('1fill')

class stretch(Command):
    args = 'num:dimen'

class newlength(Command):
    args = 'name:cs'
    def invoke(self, tex):
        tex.context.newdimen(self.parse(tex)['name'])

class setlength(Command):
    args = 'name:cs len:nox'
#   def invoke(self, tex):
#       a = self.parse(tex)
#       tex.context[a['name']].setlength(a['len'])

class addtolength(Command):
    args = 'name:cs len:nox'
#   def invoke(self, tex):
#       a = self.parse(tex)
#       tex.context[a['name']].addtolength(a['len'])

class settowidth(Command):
    args = 'name:cs text'
    
class settoheight(Command):
    args = 'name:cs text'

class settodepth(Command):
    args = 'name:cs text'
    

