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
    unicode = u'\u2009'

class InterWordSpace(Command):
    macroName = ' '
    unicode = u' '

class NoLineBreak(Command):
    macroName = 'active::~'
    unicode = u'\u00A0'

class EndOfSentence(Command):
    macroName = '@'
    unicode = u''

class frenchspacing(Command): 
    pass

class nonfrenchspacing(Command):
    pass

#
# Special characters
#

class Dollar(Command):
    macroName = '$'
    unicode = '$'

class Percent(Command):
    macroName = '%'
    unicode = '%'

class LeftBrace(Command):
    macroName = '{'
    unicode = '{'

class Underscore(Command):
    macroName = '_'
    unicode = '_'

class Ampersand(Command):
    macroName = '&'
    unicode = '&'

class HashMark(Command):
    macroName = '#'
    unicode = '#'

class RightBrace(Command):
    macroName = '}'
    unicode = '}'

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

