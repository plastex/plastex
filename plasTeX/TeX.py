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

import string
from Utils import *
from Context import Context 
from Tokenizer import Tokenizer, Token
from plasTeX import TeXFragment, TeXDocument
from plasTeX import Macro, Glue, Muglue, Mudimen, Dimen
from plasTeX.Logging import getLogger, disableLogging

# Only export the TeX class
__all__ = ['TeX']

log = getLogger()
tokenlog = getLogger('parse.tokens')
digestlog = getLogger('parse.digest')

class tokiter(object):
    """ Token iterator """
    def __init__(self, obj):
        self.obj = obj
    def __iter__(self):
        return self
    def next(self):
        return self.obj.nexttok()

class nodeiter(object):
    """ Node iterator """
    def __init__(self, obj):
        self.obj = obj
    def __iter__(self):
        return self
    def next(self):
        return self.obj.nextnode()

class bufferediter(object):
    """ Buffered iterator """
    def __init__(self, obj):
        self.obj = iter(obj)
        self.buffer = []
    def __iter__(self):
        return self
    def next(self):
        if self.buffer:
            return self.buffer.pop()
        return self.obj.next()
    def push(self, value):
        self.buffer.append(value)


class EndTokens(Token):
    """
    Demarcates the end of a stream of tokens to be processed

    When this token is reached, the TeX processor should throw
    a StopIteration exception.  This is used to process short
    sub-streams of tokens.  These tokens should never make it to
    the output stream.

    """


class TeX(object):
    """
    TeX Stream

    This class is the central TeX engine that does all of the 
    parsing, invoking of macros, etc.

    """

    def __init__(self, source=None):
        self.context = Context(self)
        self.context.loadBaseMacros()

        # Input source stack
        self.inputs = []

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
            'cs': self.castControlSequence,
            'nox': lambda x,**y: x,

            # These are handled natively
#           'args': ...,
#           'tok': ...,
#           'xtok': ...,
#           'dimen': ...,
#           'number': ...,
#           'length': ...,
#           'glue': ...,
#           'muglue': ...,
#           'mudimen': ...,
#           'mulength': ...,
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

    def filename(self):
        return self.inputs[-1].filename 
    filename = property(filename)

    def linenumber(self):
        return self.inputs[-1].linenumber
    linenumber = property(linenumber)

    def lineinfo(self):
        return ' in %s on line %s' % (self.filename, self.linenumber)
    lineinfo = property(lineinfo)

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
        while self.inputs:
            for t in self.inputs[-1]:
                t.contextDepth = self.context.depth
                return t
            self.endinput()
        raise StopIteration

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
#           if token is not None:
#               tokenlog.debug('input %s (%s, %s)', repr(token), token.catcode, 
#                                                len(self.inputs))
            if token is None:
                continue
            elif token is EndTokens:
                break
            elif token.nodeType == Node.ELEMENT_NODE:
                pass
            elif token.macroName is not None:
                try:
                    # By default, invoke() should put the macro instance
                    # itself into the output stream.  We'll handle this
                    # automatically here if `None' is received.  If you
                    # really don't want anything in the output stream,
                    # just return `[ ]'.
                    obj = self.context[token.macroName]
                    tokens = obj.invoke(self)
                    if tokens is None:
                        self.pushtoken(obj)
                    elif tokens:
                        self.pushtokens(tokens)
                    continue
                except:
                    log.error('Error while expanding "%s"%s'
                              % (token.macroName, self.lineinfo))
                    raise
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
        return self.parse([x for x in self])

    def tokenize(self, s):
        """
        Tokenize a string

        """
        return [x for x in Tokenizer(s, self.context)]

    def begingroup(self):
        self.pushtoken(BeginGroup('{'))

    def endgroup(self):
        self.pushtoken(EndGroup('}'))

    def pushtoken(self, token):
        """
        Push a token back into the token buffer to be re-read

        This method also pops an item off of the output token stream.

        Required Arguments:
        token -- token to push back

        """
        if token is not None:
            if not self.inputs:
                self.input([token])
            else:
                self.inputs[-1].pushtoken(token)

    def pushtokens(self, tokens):
        """
        Push a list of tokens back into the token buffer to be re-read

        Required Arguments:
        tokens -- list of tokens

        """
        if tokens:
            if not self.inputs:
                self.input(tokens)
            else:
                self.inputs[-1].pushtokens(tokens)

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
            if t.catcode not in [Token.CC_LETTER, Token.CC_OTHER, 
                                 Token.CC_EGROUP, Token.CC_BGROUP, 
                                 Token.CC_SPACE]:
                return tokens
        return (u''.join([x for x in tokens 
                          if x.catcode not in [Token.CC_EGROUP, 
                                               Token.CC_BGROUP]])).strip()

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

        # Check for internal TeX types first
        if type in ['dimen','length']:
            o = self.readDimen()
            return o, repr(o)

        if type in ['mudimen','mulength']:
            o = self.readMudimen()
            return o, repr(o)

        if type in ['glue']:
            o = self.readGlue()
            return o, repr(o)

        if type in ['muglue']:
            o = self.readMuglue()
            return o, repr(o)

        if type in ['number']:
            o = self.readNumber()
            return o, repr(o)

        if type in ['tok']:
            for tok in self.itertokens():
                return tok, repr(tok)

        if type in ['xtok']:
            for tok in self.itertokens():
                tok = self.expandtokens([tok])
                if len(tok) == 1:
                    return tok[0], repr(tok[0])
                return tok, self.source(tok)

        if type in ['cs']:
            expanded = False

        # Definition argument string
        if type in ['args']:
            args = []
            for t in self.itertokens():
                if t.catcode == Token.CC_BGROUP:
                    self.pushtoken(t)
                    break
                else:
                    args.append(t) 
            else: pass
            return args, self.source(args)

        tokens = self.itertokens()

        # Get a TeX token (i.e. {...})
        if spec is None:
            for t in tokens:
                toks = []
                source = [t]
                # A { ... } grouping was found
                if t.catcode == Token.CC_BGROUP:
                    level = 1
                    for t in tokens:
                        source.append(t)
                        if t.catcode == Token.CC_BGROUP:
                            toks.append(t)
                            level += 1
                        elif t.catcode == Token.CC_EGROUP:
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

    def castControlSequence(self, tokens, **kwargs):
        """
        Limit the argument to a single non-space token

        Required Arguments:
        tokens -- list of tokens to cast

        See Also:
        self.getArgument()
        self.cast()

        """
        return [x for x in tokens if x.catcode == Token.CC_ESCAPE].pop(0)

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
            elif current.catcode == Token.CC_BGROUP:
                level = 1
                listarg[-1].append(current)
                while tokens:
                    current = tokens.pop(0)
                    if current.catcode == Token.CC_BGROUP:
                        level += 1
                    elif current.catcode == Token.CC_EGROUP:
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
            if current.catcode == Token.CC_BGROUP:
                level = 1
                currentvalue.append(current)
                while tokens:
                    current = tokens.pop(0)
                    if current.catcode == Token.CC_BGROUP:
                        level += 1
                    elif current.catcode == Token.CC_EGROUP:
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

    def parse(self, tokens=None):
        """ Parse stream content until it is empty """
        outputclass = TeXFragment
        if tokens is None:
            outputclass = TeXDocument
            tokens = self
        tokens = bufferediter(tokens)
        output = []
        for item in tokens:
            item.digest(tokens)
            output.append(item)
        return outputclass(output)

#
# Parsing helper methods for parsing numbers, spaces, dimens, etc.
#

    def readOptionalSpaces(self):
        """ Remove all whitespace """
        tokens = []
        for t in self.itertokens():
            if t is None or t == '':
                continue
            elif t.catcode != Token.CC_SPACE:
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
            if t.nodeType == Node.ELEMENT_NODE:
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
            if t.nodeType == Node.ELEMENT_NODE:
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
            elif t is None or t == '' or t.catcode == Token.CC_SPACE:
                continue
            else:
                self.pushtoken(t)
                break
        return sign

    def readOneOptionalSpace(self):
        for t in self.itertokens():
            if t is None or t == '':
                continue
            if t.catcode == Token.CC_SPACE:
                return t
            self.pushtoken(t)
            return None

    def readSequence(self, chars, optspace=True, default=''):
        output = []
        for t in self:
            if t.nodeType == Node.ELEMENT_NODE:
                self.pushtoken(t)
                break 
            if t not in chars:
                if optspace and t.catcode == Token.CC_SPACE:
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
            if t.nodeType == Node.ELEMENT_NODE:
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
                for t in self.itertokens():
                    return sign * ord(t)
            break
        raise ValueError, 'Could not find integer'

    readNumber = readInteger

    def readGlue(self):
        sign = self.readOptionalSigns()
        # internal/coerced glue
        for t in self:
            if t.nodeType == Node.ELEMENT_NODE:
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
            if t.nodeType == Node.ELEMENT_NODE:
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
