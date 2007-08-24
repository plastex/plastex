#!/usr/bin/env python

"""
C.3.1 Making Sentences (p170)

"""

import time
from plasTeX import Command, Environment
from plasTeX.Logging import getLogger

#
# Quotes
#
# '          Apostrophe
# `text'     Single quotes
# ``text''   Double quotes

#
# Dashes
#
# -      Intra-word
# --     Number-range
# ---    Punctuation

#
# Spacing
#

class SmallSpace(Command):
    macroName = ','

class InterWordSpace(Command):
    macroName = ' '

class NoLineBreak(Command):
    macroName = 'active::~'

class EndOfSentence(Command):
    macroName = '@'

class frenchspacing(Command): 
    pass

class nonfrenchspacing(Command):
    pass

#
# Special characters
#

class Dollar(Command):
    macroName = '$'

class Percent(Command):
    macroName = '%'

class LeftBrace(Command):
    macroName = '{'

class Underscore(Command):
    macroName = '_'

class Ampersand(Command):
    macroName = '&'

class HashMark(Command):
    macroName = '#'

class RightBrace(Command):
    macroName = '}'

#
# Logos
#

class LaTeX(Command):
    pass

class TeX(Command):
    pass

#
# Misc
#

#class today(Command):
#    unicode = time.strftime('%B %d, %Y')

class emph(Command):
    args = 'self'

class em(Environment):
    pass

