#!/usr/bin/env python

import string
from Node import Node
try: from cStringIO import StringIO
except: from StringIO import StringIO

class category(int): pass

# The 16 category codes defined by TeX
CC_ESCAPE = category(0)
CC_BGROUP = category(1)
CC_EGROUP = category(2)
CC_MATHSHIFT = category(3)
CC_ALIGNMENT = category(4)
CC_EOL = category(5)
CC_PARAMETER = category(6)
CC_SUPER = category(7)
CC_SUB = category(8)
CC_IGNORED = category(9)
CC_SPACE = category(10)
CC_LETTER = category(11)
CC_OTHER = category(12)
CC_ACTIVE = category(13)
CC_COMMENT = category(14)
CC_INVALID = category(15)

# Default TeX categories
CATEGORIES = [
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

class Token(unicode, Node):
    """
    Base class for all unexpanded TeX tokens

    """
    catcode = None       # TeX category code
    macro = None         # Macro to invoke in place of this token

    nodeType = Node.TEXT_NODE

    def __repr__(self):
        return unicode(self)

    def __cmp__(self, other):
        # Token comparison -- character and code must match
        if isinstance(other, Token):
            if self.catcode == other.catcode:
                return unicode.__cmp__(self, other)
            return category.__cmp__(self.catcode, other.catcode)
        # Not comparing to token, just do a string match
        return unicode.__cmp__(self, unicode(other))

# Array for getting token class for the corresponding catcode
TOKENCLASSES = [None] * 16

class EscapeSequence(Token):
    """
    Escape sequence token

    This token represents a TeX escape sequence.  Doing str(...)
    on this token returns the name of the escape sequence without
    the escape character.

    """
    catcode = CC_ESCAPE
    def __repr__(self):
        if self == 'par':
            return '\n\n'
        return '\\%s ' % self
    def macro(self):
        return self
    macro = property(macro)

TOKENCLASSES[CC_ESCAPE] = EscapeSequence

class BeginGroup(Token):
    """ Beginning of a TeX group """
    catcode = CC_BGROUP
    macro = 'bgroup'

TOKENCLASSES[CC_BGROUP] = BeginGroup

class EndGroup(Token):
    """ Ending of a TeX group """
    catcode = CC_EGROUP
    macro = 'egroup'

TOKENCLASSES[CC_EGROUP] = EndGroup

class MathShift(Token):
    catcode = CC_MATHSHIFT
    macro = 'mathshift'

TOKENCLASSES[CC_MATHSHIFT] = MathShift

class Alignment(Token):
    catcode = CC_ALIGNMENT
    macro = 'alignmenttab'

TOKENCLASSES[CC_ALIGNMENT] = Alignment

class EndOfLine(Token):
    catcode = CC_EOL

TOKENCLASSES[CC_EOL] = EndOfLine

class Parameter(Token):
    catcode = CC_PARAMETER

TOKENCLASSES[CC_PARAMETER] = Parameter

class Superscript(Token):
    catcode = CC_SUPER
    macro = 'superscript'

TOKENCLASSES[CC_SUPER] = Superscript

class Subscript(Token):
    catcode = CC_SUB
    macro = 'subscript'

TOKENCLASSES[CC_SUB] = Subscript

class Space(Token):
    catcode = CC_SPACE

TOKENCLASSES[CC_SPACE] = Space

class Letter(Token):
    catcode = CC_LETTER

TOKENCLASSES[CC_LETTER] = Letter

class Other(Token):
    catcode = CC_OTHER

TOKENCLASSES[CC_OTHER] = Other

class Active(Token):
    catcode = CC_ACTIVE

TOKENCLASSES[CC_ACTIVE] = Active

class Comment(Token):
    catcode = CC_COMMENT
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'

TOKENCLASSES[CC_COMMENT] = Comment

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

            if code == CC_SUPER:

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
            if code == CC_IGNORED:
                continue
            elif code == CC_INVALID:
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
            if code == CC_ESCAPE:

                # Get name of command sequence
                self.state = Tokenizer.STATE_M

                for token in chiter:
 
                    if token.catcode == CC_EOL:
                        self.pushchar(token)
                        token = EscapeSequence()

                    elif token.catcode == CC_LETTER:
                        word = [token]
                        for t in chiter:
                            if t.catcode == CC_LETTER:
                                word.append(t) 
                            else:
                                self.pushchar(t)
                                break
                        token = EscapeSequence(''.join(word))

                    else:
                        token = EscapeSequence(token)

                    if token.catcode != CC_EOL:
                        # Absorb following whitespace
                        self.state = Tokenizer.STATE_S
                        for t in chiter:
                            if t.catcode == CC_SPACE:
                                continue
                            elif t.catcode == CC_EOL:
                                continue
                            self.pushchar(t)
                            break

                    break

                else: token = EscapeSequence()

                # Check for any \let aliases
                token = self.context.lets.get(token, token)

            # End of line
            elif code == CC_EOL:
                if self.state == Tokenizer.STATE_S:
                    self.state = Tokenizer.STATE_N
                    continue
                elif self.state == Tokenizer.STATE_M:
                    token = Space(' ')
                    code = CC_SPACE
                    self.state = Tokenizer.STATE_N
                elif self.state == Tokenizer.STATE_N: 
                    if token != '\n':
                        self.linenumber += 1
                        self.readline()
                    token = EscapeSequence('par')
                    code = CC_ESCAPE

            elif code == CC_SPACE:
                if self.state in [Tokenizer.STATE_S, Tokenizer.STATE_N]:
                    continue
                self.state = Tokenizer.STATE_S
                token = Space(u' ')

            elif code == CC_COMMENT:
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

