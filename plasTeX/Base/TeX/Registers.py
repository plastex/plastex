#!/usr/bin/env python

"""
B.2 Allocation of Registers (p346)

"""

from plasTeX import Command, Environment
from plasTeX import Dimen, Glue, MuGlue, MuDimen
from plasTeX import dimen, glue, muglue, mudimen

class dimen_(Command):
    macroName = 'dimen'

class toks(Command):
    pass

class skip(Command):
    pass

class box(Command):
    pass

class TeXCount(Command):
    macroName = 'count'

class newcount(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        tex.context.newcount(self.parse(tex)['arg'])

class newdimen(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        tex.context.newdimen(self.parse(tex)['arg'])

class newskip(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        tex.context.newskip(self.parse(tex)['arg'])

class newmuskip(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        tex.context.newmuskip(self.parse(tex)['arg'])

class newbox(Command):
    args = 'name:cs'

class newtoks(Command):
    args = 'name:cs'

class newhelp(Command):
    args = 'name:cs value'

class newread(Command):
    args = 'name:cs'

class newwrite(Command):
    args = 'name:cs'

class newfam(Command):
    args = 'name:cs'

class newlanguage(Command):
    args = 'name:cs'

class maxdimen(Dimen):
    value = dimen('16383.99pt')

class hideskip(Glue):
    value = glue('-1000pt plus 1fill')

class centering(Glue):
    value = glue('0pt plus 1000pt minus 1000pt')

class newif(Command):
    args = 'name:cs'
    def invoke(self, tex):
        tex.context.newif(self.parse(tex)['name'])

