#!/usr/bin/env python

"""
C.3.4 Accents and Special Symbols (p173)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger


#
# Table 3.1: Accents
#

class Accent(Command):
    args = 'self'

class Grave(Accent):
    macroName = '`'
class Acute(Accent):
    macroName = "'"
class Circumflex(Accent):
    macroName = '^'
class Umlaut(Accent):
    macroName = '"'
class Tilde(Accent):
    macroName = '~'
class Macron(Accent):
    macroName = '='
class Dot(Accent):
    macroName = '.'
class u(Accent): pass
class v(Accent): pass
class H(Accent): pass
class t(Accent): pass
class c(Accent): pass
class d(Accent): pass
class b(Accent): pass


#
# Table 3.2: Non-English Symbols
#

class Symbol(Command):
    pass

class oe(Symbol): pass 
class OE(Symbol): pass
class ae(Symbol): pass
class AE(Symbol): pass
class aa(Symbol): pass
class AA(Symbol): pass
class o(Symbol): pass
class O(Symbol): pass
class l(Symbol): pass
class L(Symbol): pass
class ss(Symbol): pass
# ?`
# !`


#
# Special symbols
#

class dag(Symbol): pass
class ddag(Symbol): pass
class S(Symbol): pass
class P(Symbol): pass
class copyright(Symbol): pass
class pounds(Symbol): pass
