#!/usr/bin/env python

from Categories import *

MODE_NONE = 0
MODE_BEGIN = 1
MODE_END = 2

class Token(unicode):
    code = None
    macro = None
    __slots__ = []
    def __repr__(self):
        return str(self)
    def __int__(self):
        return self.code
    def __cmp__(self, other):
        # Token comparison -- character and code must match
        if isinstance(other, Token):
            if self.code == other.code:
                return unicode.__cmp__(self, other)
            return category.__cmp__(self.code, other.code)
        # Not comparing to token, just do a string match
        return unicode.__cmp__(self, unicode(other))

TOKENCLASSES = [None] * 16

class EndTokens(Token):
    code = CC_ENDTOKENS

class EscapeSequence(Token):
    code = CC_ESCAPE
    escapechar = '\\'
    def __repr__(self):
        if self == 'par':
            return '\n\n'
        return '%s%s ' % (self.escapechar, self)
    def macro(self):
        return self
    macro = property(macro)

TOKENCLASSES[CC_ESCAPE] = EscapeSequence

class BeginGroup(Token):
    code = CC_BGROUP
    macro = 'bgroup'

TOKENCLASSES[CC_BGROUP] = BeginGroup

class EndGroup(Token):
    code = CC_EGROUP
    macro = 'egroup'

TOKENCLASSES[CC_EGROUP] = EndGroup

class MathShift(Token):
    code = CC_MATHSHIFT
    macro = 'mathshift'

TOKENCLASSES[CC_MATHSHIFT] = MathShift

class Alignment(Token):
    code = CC_ALIGNMENT
    macro = 'alignmenttab'

TOKENCLASSES[CC_ALIGNMENT] = Alignment

class EndOfLine(Token):
    code = CC_EOL

TOKENCLASSES[CC_EOL] = EndOfLine

class Parameter(Token):
    code = CC_PARAMETER

TOKENCLASSES[CC_PARAMETER] = Parameter

class Superscript(Token):
    code = CC_SUPER
    macro = 'superscript'

TOKENCLASSES[CC_SUPER] = Superscript

class Subscript(Token):
    code = CC_SUB
    macro = 'subscript'

TOKENCLASSES[CC_SUB] = Subscript

class Space(Token):
    code = CC_SPACE

TOKENCLASSES[CC_SPACE] = Space

class Letter(Token):
    code = CC_LETTER

TOKENCLASSES[CC_LETTER] = Letter

class Other(Token):
    code = CC_OTHER

TOKENCLASSES[CC_OTHER] = Other

class Active(Token):
    code = CC_ACTIVE
    macro = 'active'

TOKENCLASSES[CC_ACTIVE] = Active

class Comment(Token):
    code = CC_COMMENT

TOKENCLASSES[CC_COMMENT] = Comment
