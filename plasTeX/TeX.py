#!/usr/bin/env python

"""
TeX

This module contains the facilities for parsing TeX and LaTeX source.
The `TeX' class is an iterator interface to (La)TeX source.  Simply
feed a `TeX' instance using the input method, then iterate over the 
expanded tokens through the standard Python iterator interface.

Example:
    tex = TeX()
    tex.input(open('foo.tex','r'))
    for token in tex:
        print token

"""

import string, re
from Utils import *
from Categories import *
from Token import *
from Context import Context 
from plasTeX import TeXFragment, Macro, Glue, Muglue, Mudimen, Dimen
from plasTeX.Logging import getLogger, disableLogging
try: from cStringIO import StringIO
except: from StringIO import StringIO

log = getLogger()

# Tokenizer states
STATE_S = 1
STATE_M = 2
STATE_N = 4

class tokiter(object):
    """ Token iterator """
    def __init__(self, obj):
        self.obj = obj
    def __iter__(self):
        return self
    def next(self):
        return self.obj.nexttok()

class chariter(object):
    """ Character iterator """
    def __init__(self, obj):
        self.obj = obj
    def __iter__(self):
        return self
    def next(self):
        return self.obj.nextchar()


class Tokenizer(object):

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
        self.state = STATE_N
        self._charbuffer = []
        self._tokbuffer = []
        if isinstance(source, basestring):
            source = StringIO(source)
            self.filename = '<string>'
        elif isinstance(source, file):
            self.filename = source.name
        elif isinstance(source, (tuple,list)):
            self.pushtokens(source)
            source = StringIO('')
            self.filename = '<tokens>'
        self.seek = source.seek
        self.read = source.read
        self.readline = source.readline
        self.tell = source.tell

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

            code = token.code
 
            if code == CC_EXPANDED:
                raise ValueError, 'Expanded tokens should never make it here'

            # Escape sequence
            elif code == CC_ESCAPE:

                # Get name of command sequence
                self.state = STATE_M

                for token in chiter:
 
                    if token.code == CC_EOL:
                        self.pushchar(token)
                        token = EscapeSequence()

                    elif token.code == CC_LETTER:
                        word = [token]
                        for t in chiter:
                            if t.code == CC_LETTER:
                                word.append(t) 
                            else:
                                self.pushchar(t)
                                break
                        token = EscapeSequence(u''.join(word))

                    else:
                        token = EscapeSequence(token)

                    if token.code != CC_EOL:
                        # Absorb following whitespace
                        self.state = STATE_S
                        for t in chiter:
                            if t.code == CC_SPACE:
                                continue
                            elif t.code == CC_EOL:
                                continue
                            self.pushchar(t)
                            break

                    break

                else: token = EscapeSequence()

            # End of line
            elif code == CC_EOL:
                if self.state == STATE_S:
                    self.state = STATE_N
                    continue
                elif self.state == STATE_M:
                    token = Space(u' ')
                    code = CC_SPACE
                    self.state = STATE_N
                elif self.state == STATE_N: 
                    if token != '\n':
                        self.readline()
                    token = EscapeSequence('par')
                    code = CC_ESCAPE

            elif code == CC_SPACE:
                if self.state in [STATE_S, STATE_N]:
                    continue
                self.state = STATE_S
                token = Space(u' ')

            elif code == CC_COMMENT:
                self.readline() 
                self.state = STATE_N
                continue

            else:
                self.state = STATE_M

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


class TeX(object):
    """
    TeX Stream

    This class is the central TeX engine that does all of the 
    parsing, invoking of macros, etc.

    """

    def __init__(self, source=None):
        self.context = Context

        # Input source stack
        self.inputs = []

        # Output token stream
        self.output = []

        # TeX arguments types and their casting functions
        self.argtypes = {
            str: self.castString,
            int: self.castInteger,
            float: self.castFloat,
            list: self.castList,
            dict: self.castDictionary,
            'chr': self.castString,
            'int': self.castInteger,
            'float': self.castFloat,
            'number': self.castFloat,
            'list': self.castList,
            'dict': self.castDictionary,
            'str': self.castString,
            'chr': self.castString,
            'cs': self.castToken,
            'nox': lambda x,**y: x,
        }

        # Starting parsing if a source was given
        if source is not None:
            self.input(source)

    def input(self, source):
        """
        Add a new input source to the stack

        Required Arguments:
        source -- can be a string containing TeX source, a file object
            which contains TeX source, or a list of tokens

        """
        self.inputs.append(Tokenizer(source, self.context))

    def endinput(self):
        """ Pop the most recent input source from the stack """
        self.inputs.pop()

    def disableLogging(cls):
        """ Turn off logging """
        disableLogging()
    disableLogging = classmethod(disableLogging)

    def itertokens(self):
        """
        Create unexpanded token iterator 

        See Also:
        self.next()

        """      
        return tokiter(self)

    def nexttok(self):
        """ 
        Iterate over unexpanded tokens

        Returns:
        next unexpanded token in the stream

        """
        if not self.inputs:
            raise StopIteration
        for t in self.inputs[-1]:
            return t
        self.endinput()

    def __iter__(self):
        """
        Create expanded token iterator 

        See Also:
        self.next()

        """
        return self

    def next(self):
        """ 
        Iterate over tokens while expanding them 

        Returns:
        next expanded token in the stream

        """
        for token in self.itertokens():
            if token is None or token == '':
                continue
            elif token.code == CC_ENDTOKENS:
                break
            elif token.code == CC_EXPANDED:
                pass
            elif token.macro is not None:
                self.pushtokens(self.context[token.macro].invoke(self))
                continue
            self.output.append(token)
            return token
        raise StopIteration

    def expandtokens(self, tokens):
        """
        Expand a list of unexpanded tokens

        Required Arguments:
        tokens -- list of tokens

        Returns:
        list of expanded tokens

        """
        self.pushtoken(EndTokens)
        self.pushtokens(tokens)
        output = []
        for token in self:
            output.append(token)
        return output

    def pushtoken(self, token):
        """
        Push a token back into the token buffer to be re-read

        This method also pops an item off of the output token stream.

        Required Arguments:
        token -- token to push back

        """
        if token is not None:
            if self.output:
                self.output.pop()
            self.inputs[-1].pushtoken(token)

    def pushtokens(self, tokens):
        """
        Push a list of tokens back into the token buffer to be re-read

        Required Arguments:
        tokens -- list of tokens

        """
        if tokens:
            tokens = list(tokens)
            tokens.reverse()
            top = self.inputs[-1]
            for t in tokens:
                top.pushtoken(t)

    def source(self, tokens):
        """ 
        Return the TeX source representation of the tokens

        Required Arguments:
        tokens -- list of tokens

        Returns:
        string containing the TeX source

        """
        return u''.join([repr(x) for x in tokens])

    def normalize(self, tokens, strip=False):
        """
        Join consecutive character tokens into a string

        Required Arguments:
        tokens -- list of tokens

        Keyword Arguments:
        strip -- boolean indicating whether leading and trailing 
            whitespace should be stripped

        Returns:
        string unless the tokens contain values that cannot be casted
        to a string.  In that case, the original tokens are returned.

        """
        if tokens is None:
            return tokens
        for t in tokens:
            if t.code not in [CC_LETTER, CC_OTHER, CC_EGROUP, 
                              CC_BGROUP, CC_SPACE]:
                return tokens
        return (u''.join([x for x in tokens 
                          if x.code not in [CC_EGROUP, CC_BGROUP]])).strip()

    def getCase(self, which):
        """
        Return the requested portion of the `if' block

        Required Arguments:
        which -- the case to return.  If this is a boolean, a value of 
            `True' will return the first part of the `if' block.  If it
            is `False', it will return the `else' portion.  If this is 
            an integer, the `case' matching this integer will be returned.

        Returns:
        list of tokens from the requested portion of the `if' block

        """
        # Since the true content always comes first, we need to set
        # True to case 0 and False to case 1.
        elsefound = False
        if isinstance(which, bool):
            if which: which = 0
            else: which = 1
        cases = [[]]
        nesting = 0
        for t in self.itertokens():
            # This is probably going to cause some trouble, there 
            # are bound to be macros that start with 'if' that aren't
            # actually 'if' constructs...
            if t.startswith('if'):
                nesting += 1
            elif t == 'fi':
                if not nesting:
                    break
                nesting -= 1
            elif not(nesting) and t == 'else':
                cases.append([])
                elsefound = True
                continue
            elif not(nesting) and t == 'or':
                cases.append([])
                continue
            cases[-1].append(t)
        if not elsefound:
            cases.append([])
        return cases[which]

    def getArgument(self, *args, **kwargs):
        """
        Return and argument without the TeX source that created it

        See Also:
        self.getArgumentAndSource()

        """
        return self.getArgumentAndSource(*args, **kwargs)[0]

    def getArgumentAndSource(self, spec=None, type=None, delim=',', 
                             expanded=False, default=None):
        """ 
        Get an argument and the TeX source that created it

        Optional Arguments:
        spec -- string containing information about the type of
            argument to get.  If it is 'None', the next token is
            returned.  If it is a two-character string, a grouping
            delimited by those two characters is returned (i.e. '[]').
            If it is a single-character string, the stream is checked
            to see if the next character is the one specified.  
            In all cases, if the specified argument is not found,
            'None' is returned.
        type -- data type to cast the argument to.  New types can be
            added to the self.argtypes dictionary.  The key should
            match this 'type' argument and the value should be a callable
            object that takes a list of tokens as the first argument
            and a list of unspecified keyword arguments (i.e. **kwargs)
            for type specific information such as list delimiters.
        delim -- item delimiter for list and dictionary types
        expanded -- boolean indicating whether the argument content
            should be expanded or just returned as an unexpanded 
            text string

        Returns:
        tuple where the first argument is:

        None -- if the argument wasn't found
        object of type `type` -- if `type` was specified
        list of tokens -- for all other arguments

        The second argument is a string containing the TeX source 
        for the argument.

        """
        self.readOptionalSpaces()

        tokens = self.itertokens()

        # Get a TeX token (i.e. {...})
        if spec is None:
            for t in tokens:
                toks = []
                source = [t]
                # A { ... } grouping was found
                if t.code == CC_BGROUP:
                    level = 1
                    for t in tokens:
                        source.append(t)
                        if t.code == CC_BGROUP:
                            toks.append(t)
                            level += 1
                        elif t.code == CC_EGROUP:
                            level -= 1
                            if level == 0:
                                break
                            toks.append(t)
                        else:
                            toks.append(t)
                else:
                    toks.append(t)
                if expanded:
                    toks = self.expandtokens(toks)
                return self.cast(toks, type, delim), self.source(source)
            else: 
                return default, ''

        # Get a single character argument
        elif len(spec) == 1:
            for t in tokens:
                if t == spec:
                    return t, self.source([t])
                else:
                    self.pushtoken(t)
                    break
            return default, '' 

        # Get an argument grouped by the given characters (e.g. [...], (...))
        elif len(spec) == 2:
            begin = spec[0]
            end = spec[1]
            source = []
            for t in tokens:
                toks = []
                source = [t]
                # A [ ... ], ( ... ), etc. grouping was found
                if t == begin:
                    level = 1
                    for t in tokens:
                        source.append(t)
                        if t == begin:
                            toks.append(t)
                            level += 1
                        elif t == end:
                            level -= 1
                            if level == 0:
                                break
                            toks.append(t)
                        else:
                            toks.append(t)
                else:
                    self.pushtoken(t)
                    return default, ''
                if expanded:
                    toks = self.expandtokens(toks)
                return self.cast(toks, type, delim), self.source(source)
            return default, ''

        raise ValueError, 'Unrecognized specifier "%s"' % spec

    def cast(self, tokens, dtype, delim=','):
        """ 
        Cast the tokens to the appropriate type

        This method is used to convert tokens into Python objects.
        This happens when the user has specified that a macro argument
        should be a dictionary (i.e. %foo or foo:dict), 
        a list (i.e. @foo or foo:list), etc.

        Required Arguments:
        tokens -- list of raw, unflattened and unnormalized tokens
        dtype -- reference to the requested datatype

        Optional Arguments:
        delim -- delimiter character for list and dictionary types

        Returns:
        object of the specified type

        """
        if dtype is None:
            return tokens

        if not self.argtypes.has_key(dtype):
            log.warning('Could not find datatype "%s"' % dtype)
            return tokens

        return self.argtypes[dtype](tokens, delim=delim)

    def castToken(self, tokens, type=CC_ESCAPE, **kwargs):
        """
        Limit the argument to tokens of the requested catcode

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the category code to match tokens against

        Returns:
        list of tokens matching catcode, or if there is only one
        token in the list just that token will be returned

        See Also:
        self.getArgument()
        self.cast()

        """
        arg = [x for x in tokens if x.code == type]
        if len(arg) == 1:
            return arg.pop(0)
        return arg

    def castString(self, tokens, type=unicode, **kwargs):
        """
        Join the tokens into a string

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the string class to use for the returned object

        Returns:
        string

        See Also:
        self.getArgument()
        self.cast()

        """
        return unicode(self.normalize(tokens, strip=True))
        
    def castInteger(self, tokens, type=int, **kwargs):
        """
        Join the tokens into a string and turn the result into an integer

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the integer class to use for the returned object

        Returns:
        integer

        See Also:
        self.getArgument()
        self.cast()

        """
        return int(self.normalize(tokens, strip=True))
        
    def castFloat(self, tokens, type=float, **kwargs):
        """
        Join the tokens into a string and turn the result into a float

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the float class to use for the returned object

        Returns:
        float

        See Also:
        self.getArgument()
        self.cast()

        """
        return float(self.normalize(tokens, strip=True))
        
    def castList(self, tokens, type=list, **kwargs):
        """
        Parse items delimited by the given delimiter into a list

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the list class to use for the returned object
        delim -- the delimiter that separates each element of the list.
            The default delimiter is ','.

        Returns:
        list

        See Also:
        self.getArgument()
        self.cast()

        """
        delim = kwargs.get('delim',',')
        listarg = [[]]
        while tokens:
            current = tokens.pop(0)

            # Item delimiter
            if current == delim:
                listarg.append([])

            # Found grouping
            elif current.code == CC_BGROUP:
                level = 1
                listarg[-1].append(current)
                while tokens:
                    current = tokens.pop(0)
                    if current.code == CC_BGROUP:
                        level += 1
                    elif current.code == CC_EGROUP:
                        level -= 1
                        if not level:
                            break
                    listarg[-1].append(current)
                listarg[-1].append(current)

            else:
                listarg[-1].append(current) 

        return type([self.normalize(x,strip=True) for x in listarg])

    def castDictionary(self, tokens, type=dict, **kwargs):
        """
        Parse key/value pairs into a dictionary

        Required Arguments:
        tokens -- list of tokens to cast

        Keyword Arguments:
        type -- the dictionary class to use for the returned object
        delim -- the delimiter that separates each element of the list.
            The default delimiter is ','.

        Returns:
        dictionary

        See Also:
        self.getArgument()
        self.cast()

        """      
        delim = kwargs.get('delim',',')
        dictarg = type()
        currentkey = []
        currentvalue = None
        while tokens:
            current = tokens.pop(0)

            # Found grouping
            if current.code == CC_BGROUP:
                level = 1
                currentvalue.append(current)
                while tokens:
                    current = tokens.pop(0)
                    if current.code == CC_BGROUP:
                        level += 1
                    elif current.code == CC_EGROUP:
                        level -= 1
                        if not level:
                            break
                    currentvalue.append(current)
                currentvalue.append(current)
                continue

            # Found end-of-key delimiter
            if current == '=':
                currentvalue = []

            # Found end-of-value delimiter
            elif current == delim:
                # Handle this later
                pass

            # Extend key
            elif currentvalue is None:
                currentkey.append(current)

            # Extend value
            else:
                currentvalue.append(current)

            # Found end-of-value delimiter
            if current == delim or not tokens:
                currentkey = self.normalize(currentkey, strip=True)
                currentvalue = self.normalize(currentvalue)
                dictarg[currentkey] = currentvalue
                currentkey = []
                currentvalue = None

        return dictarg
    
    def parse(self):
        """ Parse stream content until it is empty """
        return [x for x in self]

#
# Parsing helper methods for parsing numbers, spaces, dimens, etc.
#

    def readOptionalSpaces(self):
        """ Remove all whitespace """
        tokens = []
        for t in self.itertokens():
            if t is None or t == '':
                continue
            elif t.code != CC_SPACE:
                self.pushtoken(t)
                break 
            tokens.append(t)
        return tokens

    def readKeyword(self, words, optspace=True):
        self.readOptionalSpaces()
        for word in words:
            matched = []
            letters = list(word.upper())
            for t in self.itertokens():
                matched.append(t)
                if t.upper() == letters[0]:
                    letters.pop(0)
                    if not letters:
                        if optspace: 
                            self.readOneOptionalSpace()
                        return word
                else:
                    break
            self.pushtokens(matched)
        return None

    def readDecimal(self):
        sign = self.readOptionalSigns()
        for t in self:
            if t in string.digits:
                num = t + self.readSequence(string.digits, False)
                for t in self:
                    if t in '.,':
                        num += '.' + self.readSequence(string.digits, default='0')
                    else:
                        self.pushtoken(t)
                        return sign * float(num)
                    break
                return sign * float(num)
            if t in '.,':
                return sign * float('.' + self.readSequence(string.digits, default='0'))
            if t in '\'"`':
                self.pushtoken(t)
                return sign * self.readInteger()
            break
        raise ValueError, 'Could not find decimal constant'

    def readDimen(self, units=Dimen.units):
        sign = self.readOptionalSigns()
        for t in self:
            if t.code == CC_EXPANDED:
                return Dimen(sign * dimen(t))
            self.pushtoken(t)
            break
        return Dimen(sign * self.readDecimal() * self.readUnitOfMeasure(units=units))

    def readMudimen(self):
        return Mudimen(self.readDimen(units=Mudimen.units))

    def readUnitOfMeasure(self, units):
        self.readOptionalSpaces()
        # internal unit
        for t in self:
            if t.code == CC_EXPANDED:
                return dimen(t)
            self.pushtoken(t)
            break
        true = self.readKeyword(['true'])
        unit = self.readKeyword(units)
        if unit is None:
            raise ValueError, 'Could not find unit from list %s' % units
        return Dimen('1%s' % unit)

    def readOptionalSigns(self):
        sign = 1
        self.readOptionalSpaces()
        for t in self:
            if t == '+':
                pass
            elif t == '-':
                sign = -sign
            elif t is None or t == '' or t.code == CC_SPACE:
                continue
            else:
                self.pushtoken(t)
                break
        return sign

    def readOneOptionalSpace(self):
        for t in self.itertokens():
            if t is None or t == '':
                continue
            if t.code == CC_SPACE:
                return t
            self.pushtoken(t)
            return None

    def readSequence(self, chars, optspace=True, default=''):
        output = []
        for t in self:
            if t.code == CC_EXPANDED:
                self.pushtoken(t)
                break 
            if t not in chars:
                if optspace and t.code == CC_SPACE:
                    pass
                else:
                    self.pushtoken(t)
                break
            output.append(t)
        if not output:
            return default
        return ''.join(output)

    def readInteger(self):
        sign = self.readOptionalSigns()
        for t in self:
            # internal/coerced integers
            if t.code == CC_EXPANDED:
                return sign * int(t)
            # integer constant
            if t in string.digits:
                return sign * int(t + self.readSequence(string.digits))
            # octal constant
            if t == "'":
                return sign * int('0' + self.readSequence(string.octdigits, default='0'), 8)
            # hex constant
            if t == '"':
                return sign * int('0x' + self.readSequence(string.hexdigits, default='0'), 16)
            # character token
            if t == '`':
                digits = []
                for t in self:
                    digits.append(t)
                    break
                return sign * int(ord(''.join(digits)))
            break
        raise ValueError, 'Could not find integer'

    def readGlue(self):
        sign = self.readOptionalSigns()
        # internal/coerced glue
        for t in self:
            if t.code == CC_EXPANDED:
                return Glue(sign * glue(t))
            self.pushtoken(t)
            break
        dim = self.readDimen()
        stretch = self.readStretch()
        shrink = self.readShrink()
        return Glue(sign*dim, stretch, shrink)

    def readStretch(self):
        if self.readKeyword(['plus']):
            return self.readDimen(units=Dimen.units+['filll','fill','fil'])
        return None
            
    def readShrink(self):
        if self.readKeyword(['minus']):
            return self.readDimen(units=Dimen.units+['filll','fill','fil'])
        return None

    def readMuglue(self):
        sign = self.readOptionalSigns()
        # internal/coerced muglue
        for t in self:
            if t.code == CC_EXPANDED:
                return Muglue(sign * muglue(t))
            self.pushtoken(t)
            break
        dim = self.readMudimen()
        stretch = self.readMustretch()
        shrink = self.readMushrink()
        return Muglue(sign*dim, stretch, shrink)

    def readMustretch(self):
        if self.readKeyword(['plus']):
            return self.readDimen(units=Mudimen.units+['filll','fill','fil'])
        return None
            
    def readMushrink(self):
        if self.readKeyword(['minus']):
            return self.readDimen(units=Mudimen.units+['filll','fill','fil'])
        return None
