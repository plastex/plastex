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
VERBATIM_CATEGORIES[11] = string.letters

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

    def __repr__(self):
        return self.source

    def __cmp__(self, other):
        # Token comparison -- character and code must match
        if isinstance(other, Token):
            if self.catcode == other.catcode:
                return cmp(unicode(self), unicode(other))
            return cmp(self.catcode, other.catcode)
        # Not comparing to token, just do a string match
        return cmp(unicode(self), unicode(other))

    @property
    def source(self):
        return self


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
        # Handle active character format
        if '::' in self:
            return self.split('::').pop()
        return '\\%s ' % self
    source = property(source)
    def macroName(self):
        return self
    macroName = property(macroName)

class BeginGroup(Token):
    """ Beginning of a TeX group """
    catcode = Token.CC_BGROUP
    macroName = 'bgroup'

class EndGroup(Token):
    """ Ending of a TeX group """
    catcode = Token.CC_EGROUP
    macroName = 'egroup'

class MathShift(Token):
    catcode = Token.CC_MATHSHIFT
    macroName = 'active::$'

class Alignment(Token):
    catcode = Token.CC_ALIGNMENT
    macroName = 'active::&'

class EndOfLine(Token):
    catcode = Token.CC_EOL
    isElementContentWhitespace = True

class Parameter(Token):
    catcode = Token.CC_PARAMETER

class Superscript(Token):
    catcode = Token.CC_SUPER
    macroName = 'active::^'

class Subscript(Token):
    catcode = Token.CC_SUB
    macroName = 'active::_'

class Space(Token):
    catcode = Token.CC_SPACE
    isElementContentWhitespace = True

class Letter(Token):
    catcode = Token.CC_LETTER

class Other(Token):
    catcode = Token.CC_OTHER

class Active(Token):
    catcode = Token.CC_ACTIVE

class Comment(Token):
    catcode = Token.CC_COMMENT
    nodeType = Node.COMMENT_NODE
    nodeName = '#comment'
    isElementContentWhitespace = True

class Tokenizer(object):

    # Tokenizer states
    STATE_S = 1
    STATE_M = 2
    STATE_N = 4

    # Array for getting token class for the corresponding catcode
    tokenClasses = [None] * 16
    tokenClasses[Token.CC_ESCAPE] = EscapeSequence
    tokenClasses[Token.CC_BGROUP] = BeginGroup
    tokenClasses[Token.CC_EGROUP] = EndGroup
    tokenClasses[Token.CC_MATHSHIFT] = MathShift
    tokenClasses[Token.CC_ALIGNMENT] = Alignment
    tokenClasses[Token.CC_EOL] = EndOfLine
    tokenClasses[Token.CC_PARAMETER] = Parameter
    tokenClasses[Token.CC_SUPER] = Superscript
    tokenClasses[Token.CC_SUB] = Subscript
    tokenClasses[Token.CC_SPACE] = Space
    tokenClasses[Token.CC_LETTER] = Letter
    tokenClasses[Token.CC_OTHER] = Other
    tokenClasses[Token.CC_ACTIVE] = Active
    tokenClasses[Token.CC_COMMENT] = Comment

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
#       self.readline = source.readline
        self.tell = source.tell
        self.linenumber = 1

# There seems to be a problem with readline in Python 2.4 !!!
    def readline(self):
        read = self.read
        while 1:
            char = read(1)
            if not char or ord(char) == 10:
                break

    def iterchars(self):
        """ 
        Get the next character in the stream and its category code

        This function handles automatically converts characters like
        ^^M, ^^@, etc. into the correct character.  It also bypasses
        ignored and invalid characters. 

        If you are iterating through the characters in a TeX instance
        and you go too far, you can put the character back with
        the pushchar() method.

        """
        # Create locals before going into the generator loop
        buffer = self._charbuffer
        classes = self.tokenClasses
        read = self.read
        seek = self.seek
        whichCode = self.context.whichCode
        CC_SUPER = Token.CC_SUPER
        CC_IGNORED = Token.CC_IGNORED
        CC_INVALID = Token.CC_INVALID

        while 1:
            while buffer:
                yield buffer.pop(0)

            token = read(1)

            if not token:
                break

            # ord(token) == 10 is the same as saying token == '\n'
            # but it is much faster.
            if ord(token) == 10:
                self.linenumber += 1

            code = whichCode(token)

            if code == CC_SUPER:

                # Handle characters like ^^M, ^^@, etc.
                char = read(1)

                if char == token:
                    char = read(1)
                    num = ord(char)
                    if num >= 64: token = chr(num-64)
                    else: token = chr(num+64)
                    code = whichCode(token)

                else:
                    seek(-1,1)

            # Just go to the next character if you see one of these...
            if code == CC_IGNORED or code == CC_INVALID:
                continue

            yield classes[code](token)

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

    def __iter__(self):
        """ 
        Iterate over tokens in the input stream

        Returns:
        generator that iterates through tokens in the stream

        """
        # Cache variables to prevent globol lookups during generator 
        global Space, EscapeSequence
        Space = Space
        EscapeSequence = EscapeSequence
        buffer = self._tokbuffer
        chariter = self.iterchars()
        next = chariter.next
        context = self.context
        pushchar = self.pushchar
        STATE_N = self.STATE_N
        STATE_M = self.STATE_M
        STATE_S = self.STATE_S
        ELEMENT_NODE = Node.ELEMENT_NODE
        CC_LETTER = Token.CC_LETTER
        CC_OTHER = Token.CC_OTHER
        CC_SPACE = Token.CC_SPACE
        CC_EOL = Token.CC_EOL
        CC_ESCAPE = Token.CC_ESCAPE
        CC_EOL = Token.CC_EOL
        CC_COMMENT = Token.CC_COMMENT
        CC_ACTIVE = Token.CC_ACTIVE
        prev = None

        while 1:

            # Purge buffer first
            while buffer:
                yield buffer.pop(0)

            # Get the next character
            token = next()

            if token.nodeType == ELEMENT_NODE:
                raise ValueError, 'Expanded tokens should never make it here'

            code = token.catcode

            # Short circuit letters and other since they are so common
            if code == CC_LETTER or code == CC_OTHER:
                self.state = STATE_M

            # Whitespace
            elif code == CC_SPACE:
                if self.state  == STATE_S or self.state == STATE_N:
                    continue
                self.state = STATE_S
                token = Space(u' ')

            # End of line
            elif code == CC_EOL:
                state = self.state
                if state == STATE_S:
                    self.state = STATE_N
                    continue
                elif state == STATE_M:
                    token = Space(' ')
                    code = CC_SPACE
                    self.state = STATE_N
                elif state == STATE_N: 
                    # ord(token) != 10 is the same as saying token != '\n'
                    # but it is much faster.
                    if ord(token) != 10:
                        self.linenumber += 1
                        self.readline()
                    token = EscapeSequence('par')
                    # Prevent adjacent paragraphs
                    if prev == token:
                        continue
                    code = CC_ESCAPE

            # Escape sequence
            elif code == CC_ESCAPE:

                # Get name of command sequence
                self.state = STATE_M

                for token in chariter:
 
                    if token.catcode == CC_LETTER:
                        word = [token]
                        for t in chariter:
                            if t.catcode == CC_LETTER:
                                word.append(t) 
                            else:
                                pushchar(t)
                                break
                        token = EscapeSequence(''.join(word))

                    elif token.catcode == CC_EOL:
                        #pushchar(token)
                        #token = EscapeSequence()
                        token = Space(' ')
                        self.state = STATE_S

                    else:
                        token = EscapeSequence(token)
#
# Because we can implement macros both in LaTeX and Python, we don't 
# always want the whitespace to be eaten.  For example, implementing
# \chardef\%=`% would be \char{`%} in TeX, but in Python it's just 
# another macro class that would eat whitspace incorrectly.  So we
# have to do this kind of thing in the parse() method of Macro.
#
                    if token.catcode != CC_EOL:
# HACK: I couldn't get the parse() thing to work so I'm just not
#       going to parse whitespace after EscapeSequences that end in
#       non-letter characters as a half-assed solution.
                        if token[-1] in string.letters:
                            # Absorb following whitespace
                            self.state = STATE_S
#

                    break

                else: token = EscapeSequence()

                # Check for any \let aliases
                token = context.lets.get(token, token)

            elif code == CC_COMMENT:
                self.readline() 
                self.linenumber += 1
                self.state = STATE_N
                continue

            elif code == CC_ACTIVE:
                token = EscapeSequence('active::%s' % token)
                token = context.lets.get(token, token)
                self.state = STATE_M

            else:
                self.state = STATE_M

            prev = token

            yield token
