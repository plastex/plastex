#!/usr/bin/env python

import string
from DOM import Node, Text
try: from cStringIO import StringIO
except: from StringIO import StringIO

# Default TeX categories
DEFAULT_CATEGORIES = [
   '\\',  # 0  - Escape character
   '{',   # 1  - Beginning of group
   '}',   # 2  - End of group
   '$',   # 3  - Math shift
   '&',   # 4  - Alignment tab
   '\n',  # 5  - End of line
   '#',   # 6  - Parameter
   '^',   # 7  - Superscript
   '_',   # 8  - Subscript
   '\x00',# 9  - Ignored character
   ' \t\r\f', # 10 - Space
   string.letters + '@', # - Letter
   '',    # 12 - Other character - This isn't explicitly defined.  If it
          #                        isn't any of the other categories, then
          #                        it's an "other" character.
   '~',   # 13 - Active character
   '%',   # 14 - Comment character
   ''     # 15 - Invalid character
]

VERBATIM_CATEGORIES = [''] * 16

class Token(Text):
    """ Base class for all TeX tokens """

    # The 16 category codes defined by TeX
    CC_ESCAPE = 0
    CC_BGROUP = 1
    CC_EGROUP = 2
    CC_MATHSHIFT = 3
    CC_ALIGNMENT = 4
    CC_EOL = 5
    CC_PARAMETER = 6
    CC_SUPER = 7
    CC_SUB = 8
    CC_IGNORED = 9
    CC_SPACE = 10
    CC_LETTER = 11
    CC_OTHER = 12
    CC_ACTIVE = 13
    CC_COMMENT = 14
    CC_INVALID = 15
    
    catcode = None       # TeX category code
    macroName = None     # Macro to invoke in place of this token

#   nodeType = Node.TEXT_NODE

    def __cmp__(self, other):
        # Token comparison -- character and code must match
        if isinstance(other, Token):
            if self.catcode == other.catcode:
                return cmp(unicode(self), unicode(other))
            return cmp(self.catcode, other.catcode)
        # Not comparing to token, just do a string match
        return cmp(unicode(self), unicode(other))

    def source(self):
        return unicode(self)
    source = property(source)

# Array for getting token class for the corresponding catcode
TOKENCLASSES = [None] * 16

class EscapeSequence(Token):
    """
    Escape sequence token

    This token represents a TeX escape sequence.  Doing str(...)
    on this token returns the name of the escape sequence without
    the escape character.

    """
    catcode = Token.CC_ESCAPE
    def source(self):
        if self == 'par':
            return '\n\n'
        return '\\%s ' % self
    source = property(source)
    def macroName(self):
        return self
    macroName = property(macroName)

TOKENCLASSES[Token.CC_ESCAPE] = EscapeSequence

class BeginGroup(Token):
    """ Beginning of a TeX group """
    catcode = Token.CC_BGROUP
    macroName = 'bgroup'

TOKENCLASSES[Token.CC_BGROUP] = BeginGroup

class EndGroup(Token):
    """ Ending of a TeX group """
    catcode = Token.CC_EGROUP
    macroName = 'egroup'

TOKENCLASSES[Token.CC_EGROUP] = EndGroup

class MathShift(Token):
    catcode = Token.CC_MATHSHIFT
    macroName = 'mathshift'

TOKENCLASSES[Token.CC_MATHSHIFT] = MathShift

class Alignment(Token):
    catcode = Token.CC_ALIGNMENT
    macroName = 'alignmenttab'

TOKENCLASSES[Token.CC_ALIGNMENT] = Alignment

class EndOfLine(Token):
    catcode = Token.CC_EOL
    isElementContentWhitespace = True

TOKENCLASSES[Token.CC_EOL] = EndOfLine

class Parameter(Token):
    catcode = Token.CC_PARAMETER

TOKENCLASSES[Token.CC_PARAMETER] = Parameter

class Superscript(Token):
    catcode = Token.CC_SUPER
    macroName = 'superscript'

TOKENCLASSES[Token.CC_SUPER] = Superscript

class Subscript(Token):
    catcode = Token.CC_SUB
    macroName = 'subscript'

TOKENCLASSES[Token.CC_SUB] = Subscript

class Space(Token):
    catcode = Token.CC_SPACE
    isElementContentWhitespace = True

TOKENCLASSES[Token.CC_SPACE] = Space

class Letter(Token):
    catcode = Token.CC_LETTER

TOKENCLASSES[Token.CC_LETTER] = Letter

class Other(Token):
    catcode = Token.CC_OTHER

TOKENCLASSES[Token.CC_OTHER] = Other

class Active(Token):
    catcode = Token.CC_ACTIVE

TOKENCLASSES[Token.CC_ACTIVE] = Active

class Comment(Token):
    catcode = Token.CC_COMMENT
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'
    isElementContentWhitespace = True

TOKENCLASSES[Token.CC_COMMENT] = Comment

class chariter(object):
    """ Character iterator """
    def __init__(self, obj):
        self.obj = obj
    def __iter__(self):
        return self
    def next(self):
        return self.obj.nextchar()

class Tokenizer(object):

    # Tokenizer states
    STATE_S = 1
    STATE_M = 2
    STATE_N = 4

    def __init__(self, source, context):
        """
        Instantiate a tokenizer

        Required Arguments:
        source -- the source to tokenize.  This can be a string containing
            TeX source, a file object that contains TeX source, or a 
            list of tokens
        context -- the document's context object

        """
        self.context = context
        self.state = Tokenizer.STATE_N
        self._charbuffer = []
        self._tokbuffer = []
        if isinstance(source, basestring):
            source = StringIO(source)
            self.filename = '<string>'
        elif isinstance(source, (tuple,list)):
            self.pushtokens(source)
            source = StringIO('')
            self.filename = '<tokens>'
        else:
            self.filename = source.name
        self.seek = source.seek
        self.read = source.read
        self.readline = source.readline
        self.tell = source.tell
        self.linenumber = 1

    def nextchar(self):
        """ 
        Get the next character in the stream and its category code

        This function handles automatically converts characters like
        ^^M, ^^@, etc. into the correct character.  It also bypasses
        ignored and invalid characters. 

        If you are iterating through the characters in a TeX instance
        and you go too far, you can put the character back with
        the pushchar() method.

        See Also:
        self.iterchars()

        """
        if self._charbuffer:
            return self._charbuffer.pop(0)

        while 1:
            token = self.read(1)

            if not token:
                raise StopIteration

            if token == '\n':
                self.linenumber += 1

            code = self.context.whichCode(token)

            if code == Token.CC_SUPER:

                # Handle characters like ^^M, ^^@, etc.
                char = self.read(1)

                if char == token:
                    char = self.read(1)
                    num = ord(char)
                    if num >= 64: token = chr(num-64)
                    else: token = chr(num+64)
                    code = self.context.whichCode(token)

                else:
                    self.seek(-1,1)

            # Just keep going if you see one of these...
            if code == Token.CC_IGNORED:
                continue
            elif code == Token.CC_INVALID:
                continue

            break

        return TOKENCLASSES[code](token)

    def pushchar(self, char):
        """ 
        Push a character back into the stream to be re-read 

        Required Arguments:
        char -- the character to push back

        """
        self._charbuffer.insert(0, char)

    def pushtoken(self, token):
        """
        Push a token back into the stream to be re-read

        Required Arguments:
        token -- token to be pushed back

        """
        if token is not None:
            self._tokbuffer.insert(0, token)

    def pushtokens(self, tokens):
        """
        Push a list of tokens back into the stream to be re-read

        Required Arguments:
        tokens -- list of tokens to push back

        """
        if tokens:
            tokens = list(tokens)
            tokens.reverse()
            for t in tokens:
                self.pushtoken(t)

    def next(self):
        """ 
        Iterate over tokens in the input stream

        Returns:
        next token in the stream

        See Also:
        self.__iter__()

        """
        if self._tokbuffer:
            return self._tokbuffer.pop(0)

        chiter = self.iterchars()

        for token in chiter:

            if token.nodeType == Node.ELEMENT_NODE:
                raise ValueError, 'Expanded tokens should never make it here'

            code = token.catcode
 
            # Escape sequence
            if code == Token.CC_ESCAPE:

                # Get name of command sequence
                self.state = Tokenizer.STATE_M

                for token in chiter:
 
                    if token.catcode == Token.CC_EOL:
                        self.pushchar(token)
                        token = EscapeSequence()

                    elif token.catcode == Token.CC_LETTER:
                        word = [token]
                        for t in chiter:
                            if t.catcode == Token.CC_LETTER:
                                word.append(t) 
                            else:
                                self.pushchar(t)
                                break
                        token = EscapeSequence(''.join(word))

                    else:
                        token = EscapeSequence(token)

                    if token.catcode != Token.CC_EOL:
                        # Absorb following whitespace
                        self.state = Tokenizer.STATE_S
                        for t in chiter:
                            if t.catcode == Token.CC_SPACE:
                                continue
                            elif t.catcode == Token.CC_EOL:
                                continue
                            self.pushchar(t)
                            break

                    break

                else: token = EscapeSequence()

                # Check for any \let aliases
                token = self.context.lets.get(token, token)

            # End of line
            elif code == Token.CC_EOL:
                if self.state == Tokenizer.STATE_S:
                    self.state = Tokenizer.STATE_N
                    continue
                elif self.state == Tokenizer.STATE_M:
                    token = Space(' ')
                    code = Token.CC_SPACE
                    self.state = Tokenizer.STATE_N
                elif self.state == Tokenizer.STATE_N: 
                    if token != '\n':
                        self.linenumber += 1
                        self.readline()
                    token = EscapeSequence('par')
                    code = Token.CC_ESCAPE

            elif code == Token.CC_SPACE:
                if self.state in [Tokenizer.STATE_S, Tokenizer.STATE_N]:
                    continue
                self.state = Tokenizer.STATE_S
                token = Space(u' ')

            elif code == Token.CC_COMMENT:
                self.readline() 
                self.linenumber += 1
                self.state = Tokenizer.STATE_N
                continue

            else:
                self.state = Tokenizer.STATE_M

            return token

        raise StopIteration

    def __iter__(self):
        """
        Return an iterator that iterates over the tokens in the input stream

        See Also:
        self.nexttok()

        """
        return self

    def iterchars(self):
        """
        Return an iterator that iterates over characters in the input stream

        See Also:
        self.nextchar()

        """
        return chariter(self)

