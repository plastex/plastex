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
from plasTeX import Parameter, Macro, glue, muglue, mudimen, dimen, number
from plasTeX.Logging import getLogger, disableLogging

# Only export the TeX class
__all__ = ['TeX']

log = getLogger()
tokenlog = getLogger('parse.tokens')
digestlog = getLogger('parse.digest')


class bufferediter(object):
    """ Buffered iterator """
    __slots__ = ['_next','_buffer']
    def __init__(self, obj):
        self._next = iter(obj).next
        self._buffer = []
    def __iter__(self):
        return self
    def next(self):
        if self._buffer:
            return self._buffer.pop()
        return self._next()
    def push(self, value):
        self._buffer.append(value)


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
            'int': self.castInteger,
            int: self.castInteger,
            'float': self.castFloat,
            float: self.castFloat,
            'double': self.castFloat,
            'number': self.castFloat,
            'str': self.castString,
            str: self.castString,
            'chr': self.castString,
            chr: self.castString,
            'char': self.castString,
            'length': self.castLength,
            'dimension': self.castLength,
            'dimen': self.castLength,
            'cs': self.castControlSequence,
            'label': self.castLabel,
            'id': self.castLabel,
            'idref': self.castRef,
            'ref': self.castRef,
            'nox': lambda x,**y: x,
            'list': self.castList,
            list: self.castList,
            'dict': self.castDictionary,
            dict: self.castDictionary,

            # These TeX primitive types are handled natively
#           'Args': ...,
#           'Tok': ...,
#           'XTok': ...,
#           'Number': ...,
#           'Dimen': ...,
#           'MuDimen': ...,
#           'Length': ...,
#           'MuLength': ...,
#           'Glue': ...,
#           'MuGlue': ...,
        }

        # Starting parsing if a source was given
        self.input(source)

    def input(self, source):
        """
        Add a new input source to the stack

        Required Arguments:
        source -- can be a string containing TeX source, a file object
            which contains TeX source, or a list of tokens

        """
        if source is None:
            return
        self.inputs.append(Tokenizer(source, self.context))

    def endinput(self):
        """ 
        Pop the most recent input source from the stack 

        Returns:
        The top item in the input stack, or None if there isn't one

        """
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
        Iterate over unexpanded tokens

        Returns:
        generator that iterates through the unexpanded tokens

        """
        # Create locals before going into generator loop
        inputs = self.inputs
        context = self.context
        endinput = self.endinput

        while inputs:
            # Always get next token from top of input stack
            for t in inputs[-1]:
                # Save context depth of each token for use in digestion
                t.contextDepth = context.depth
                yield t
            endinput()

    def __iter__(self):
        """ 
        Iterate over tokens while expanding them 

        Returns:
        generator that iterates through the expanded tokens

        """
        # Cache variables before starting the generator
        next = self.itertokens().next
        pushtoken = self.pushtoken
        pushtokens = self.pushtokens
        context = self.context
        ELEMENT_NODE = Node.ELEMENT_NODE
        CC_ACTIVE = Token.CC_ACTIVE

        while 1:
            # Get the next token
            token = next()

            # Token is null, ignore it
            if token is None:
                continue

            # Magical EndTokens flag telling us to bail out
            elif token is EndTokens:
                break

            # Macro that has already been expanded
            elif token.nodeType == ELEMENT_NODE:
                pass

            # We need to expand this one
            elif token.macroName is not None:
                try:
                    # By default, invoke() should put the macro instance
                    # itself into the output stream.  We'll handle this
                    # automatically here if `None' is received.  If you
                    # really don't want anything in the output stream,
                    # just return `[ ]'.
                    obj = context[token.macroName]
                    tokens = obj.invoke(self)
                    if tokens is None:
                        pushtoken(obj)
                    elif tokens:
                        pushtokens(tokens)
                    continue
                except:
                    log.error('Error while expanding "%s"%s'
                              % (token.macroName, self.lineinfo))
                    raise

            yield token

    def expandtokens(self, tokens):
        """
        Expand a list of unexpanded tokens

        This can be used to expand tokens in a macro argument without
        having them sent to the output stream.

        Required Arguments:
        tokens -- list of tokens

        Returns:
        `TeXFragment' populated with expanded tokens

        """
        # EndTokens is a special token that tells the token iterator
        # to stop the iteration
        self.pushtoken(EndTokens)
        self.pushtokens(tokens)

        tokens = bufferediter(self)
        output = TeXFragment()
        for item in tokens:
            item.digest(tokens)
            output.append(item)

        return output

    def parse(self):
        """ 
        Parse stream content until it is empty 

        Returns:
        `TeXDocument' instance

        """
        tokens = bufferediter(self)
        output = TeXDocument()
        for item in tokens:
            item.digest(tokens)
            output.append(item)
        return output

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
        return u''.join([x.source for x in tokens])

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
        grouptokens = [Token.CC_EGROUP, Token.CC_BGROUP]
        texttokens = [Token.CC_LETTER, Token.CC_OTHER, 
                      Token.CC_EGROUP, Token.CC_BGROUP, 
                      Token.CC_SPACE]
        for t in tokens:
            # Element nodes can't be part of normalized text
            if t.nodeType == Macro.ELEMENT_NODE:
                return tokens
            if t.catcode not in texttokens:
                return tokens
        return (u''.join([x for x in tokens 
                          if x.catcode not in grouptokens])).strip()

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
        if type in ['Dimen','Length']:
            o = self.readDimen()
            return o, o.source

        if type in ['MuDimen','MuLength']:
            o = self.readMuDimen()
            return o, o.source

        if type in ['Glue']:
            o = self.readGlue()
            return o, o.source

        if type in ['MuGlue']:
            o = self.readMuGlue()
            return o, o.source

        if type in ['Number']:
            o = self.readNumber()
            return o, o.source

        if type in ['Tok','Tok']:
            for tok in self.itertokens():
                return tok, tok.source

        if type in ['XTok','XToken']:
            for tok in self.itertokens():
                tok = self.expandtokens([tok])
                if len(tok) == 1:
                    return tok[0], tok[0].source
                return tok, tok.source

        # Definition argument string
        if type in ['Args']:
            args = []
            for t in self.itertokens():
                if t.catcode == Token.CC_BGROUP:
                    self.pushtoken(t)
                    break
                else:
                    args.append(t) 
            else: pass
            return args, self.source(args)

        if type in ['cs']:
            expanded = False

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
        return type(self.normalize(tokens, strip=True))

    def castLabel(self, tokens, **kwargs):
        """
        Join the tokens into a string a set a label in the context

        Required Arguments:
        tokens -- list of tokens to cast

        Returns:
        string

        See Also:
        self.getArgument()
        self.cast()

        """
        label = self.castString(tokens, **kwargs)
        self.context.label(label)
        return label

    def castRef(self, tokens, **kwargs):
        self.castString(self, tokens, **kwargs)
        
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
        return type(self.normalize(tokens, strip=True))
        
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
        return type(self.normalize(tokens, strip=True))

    def castLength(self, tokens, **kwargs):
        """
        Jain the tokens into a string and convert the result into a `Dimen'

        Required Arguments:
        tokens -- list of tokens to cast

        Returns:
        `Dimen' instance

        See Also:
        self.getArgument()
        self.cast()

        """
        return Dimen(self.castString(tokens, **kwargs))
        
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

            if current.nodeType == Macro.ELEMENT_NODE:
                currentvalue.append(current)
                continue

            # Found grouping
            elif current.catcode == Token.CC_BGROUP:
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

    def kpsewhich(self, name):
        """ 
        Locate the given file in a kpsewhich-like manner 

        Required Arguments:
        name -- name of file to find

        Returns:
        full path to file -- if it is found
        `None' -- if it is not found

        """
        plastexinputs = os.environ.get('PLASTEXINPUTS', '.')
        extensions = ['.sty','.tex','.cls']
        for path in plastexinputs.split(':'):
           for ext in extensions:
               fullpath = os.path.join(path, name+ext)
               if os.path.isfile(fullpath):
                   return fullpath

#
# Parsing helper methods for parsing numbers, spaces, dimens, etc.
#

    def readOptionalSpaces(self):
        """ Remove all whitespace """
        tokens = []
        for t in self.itertokens():
            if t.nodeType == t.ELEMENT_NODE:
                self.pushtoken(t)
                break
            elif t is None or t == '':
                continue
            elif t.catcode != Token.CC_SPACE:
                self.pushtoken(t)
                break 
            tokens.append(t)
        return tokens

    def readKeyword(self, words, optspace=True):
        """ 
        Read keyword from the stream

        Required Arguments:
        words -- list of possible keywords to get from the stream

        Keyword Arguments:
        optspace -- boolean indicating if it should eat an optional
            space token after a matched keyword

        Returns:
        matched keyword -- if one is found
        `None' -- if none of the keywords are found

        """
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
        """ Read a decimal number from the stream """
        sign = self.readOptionalSigns()
        for t in self:
            if t in string.digits:
                num = t + self.readSequence(string.digits, False)
                for t in self:
                    if t.nodeType == Token.ELEMENT_NODE:
                        self.pushtoken(t)
                        return sign * float(num)
                    elif t in '.,':
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

    def readDimen(self, units=dimen.units):
        """
        Read a dimension from the stream

        Keyword Arguments:
        units -- list of acceptable units of measure

        Returns:
        `dimen' instance

        """
        Parameter.enabled = False
        sign = self.readOptionalSigns()
        for t in self:
            if t.nodeType == Node.ELEMENT_NODE:
                return dimen(sign * dimen(t))
            self.pushtoken(t)
            break
        num = dimen(sign * self.readDecimal() * self.readUnitOfMeasure(units=units))
        Parameter.enabled = True
        return num

    def readMuDimen(self):
        """ Read a mudimen from the stream """
        return mudimen(self.readDimen(units=mudimen.units))

    def readUnitOfMeasure(self, units):
        """
        Read a unit of measure from the stream

        Required Arguments:
        units -- list of acceptable units of measure

        Returns:
        `dimen' instance

        """
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
        return dimen('1%s' % unit)

    def readOptionalSigns(self):
        """ 
        Read optional + and - signs 

        Returns:
        +1 or -1 

        """
        sign = 1
        self.readOptionalSpaces()
        for t in self:
            if t.nodeType == Token.ELEMENT_NODE:
                self.pushtoken(t)
                break
            elif t == '+':
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
        """ Read one optional space from the stream """
        for t in self.itertokens():
            if t.nodeType == Token.ELEMENT_NODE:
                self.pushtoken(t)
                return None
            if t is None or t == '':
                continue
            if t.catcode == Token.CC_SPACE:
                return t
            self.pushtoken(t)
            return None

    def readSequence(self, chars, optspace=True, default=''):
        """
        Read a sequence of characters from a given set

        Required Arguments:
        chars -- sequence of characters that should be accepted
        
        Keyword Arguments:
        optspace -- boolean indicating if an optional space should 
            be absorbed after the sequence of characters
        default -- string to return if none of the characters in 
            the given set are found

        Returns:
        string of characters matching those in the sequence `chars'
        or `default' if none are found

        """
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
        return u''.join(output)

    def readInteger(self):
        """
        Read an integer from the stream

        Returns:
        `number' instance

        """
        Parameter.enabled = False
        num = None
        sign = self.readOptionalSigns()
        for t in self:
            # internal/coerced integers
            if t.nodeType == Node.ELEMENT_NODE:
                num = number(sign * number(t))
            # integer constant
            elif t in string.digits:
                num = number(sign * int(t + self.readSequence(string.digits)))
            # octal constant
            elif t == "'":
                num = number(sign * int('0' + self.readSequence(string.octdigits, default='0'), 8))
            # hex constant
            elif t == '"':
                num = number(sign * int('0x' + self.readSequence(string.hexdigits, default='0'), 16))
            # character token
            elif t == '`':
                for t in self.itertokens():
                    num = number(sign * ord(t))
                    break
            break
        Parameter.enabled = True
        if num is not None:
            return num
        raise ValueError, 'Could not find integer'

    readNumber = readInteger

    def readGlue(self):
        """ Read a glue parameter from the stream """
        Parameter.enabled = False
        sign = self.readOptionalSigns()
        # internal/coerced glue
        for t in self:
            if t.nodeType == Node.ELEMENT_NODE:
                return glue(sign * glue(t))
            self.pushtoken(t)
            break
        dim = self.readDimen()
        stretch = self.readStretch()
        shrink = self.readShrink()
        Parameter.enabled = True
        return glue(sign*dim, stretch, shrink)

    def readStretch(self):
        """ Read a stretch parameter from the stream """
        if self.readKeyword(['plus']):
            return self.readDimen(units=dimen.units+['filll','fill','fil'])
        return None
            
    def readShrink(self):
        """ Read a shrink parameter from the stream """
        if self.readKeyword(['minus']):
            return self.readDimen(units=dimen.units+['filll','fill','fil'])
        return None

    def readMuGlue(self):
        """ Read a muglue parameter from the stream """
        Parameter.enabled = False
        sign = self.readOptionalSigns()
        # internal/coerced muglue
        for t in self:
            if t.nodeType == Node.ELEMENT_NODE:
                return muglue(sign * muglue(t))
            self.pushtoken(t)
            break
        dim = self.readMuDimen()
        stretch = self.readMuStretch()
        shrink = self.readMuShrink()
        Parameter.enabled = True
        return muglue(sign*dim, stretch, shrink)

    def readMuStretch(self):
        """ Read a mustretch parameter from the stream """
        if self.readKeyword(['plus']):
            return self.readDimen(units=mudimen.units+['filll','fill','fil'])
        return None
            
    def readMuShrink(self):
        """ Read a mushrink parameter from the stream """
        if self.readKeyword(['minus']):
            return self.readDimen(units=mudimen.units+['filll','fill','fil'])
        return None
