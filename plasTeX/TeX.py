#!/usr/bin/env python

import string, re
from Utils import *
from Context import Context
from plasTeX import TeXFragment, Glue, str2dimen, Dimension
from plasTeX.Logging import getLogger, disableLogging
try: from cStringIO import StringIO
except: from StringIO import StringIO

log = getLogger()
sectionlog = getLogger('parse.sections')
persistlog = getLogger('parse.persistent')
marklog = getLogger('parse.persistent.marks')
commandlog = getLogger('parse.commands')
verbatimlog = getLogger('parse.verbatim')

class EndGroup(Exception):
    """ Internal Use Only: Used for parsing TeX groups (i.e {...}) """

class EndOfFile(Exception):
    """ Internal Use Only: Reached end of input exception """

class Token(str):
    def __int__(self):
        try: return self.code
        except AttributeError: return int(str(self))
class EscapeSequence(str): pass
class MacroParameter(str): pass
class ParameterToken(str):
    code = 6


class Persistent(object):
    """ 
    Stream object for persisting TeX source 

    This stream is kept in sync with the source being read.
    When something defined by a \\def, \\newcommand, or \\newenvironment
    is reached, the definition, not the actual TeX source, is
    put into this stream.  This allows you to get the TeX source
    an command or environment in the document later.  This is 
    generally used in creating images for math or unknown environments.

    """

    def __init__(self):
        self.string = StringIO()
        self.seek = self.string.seek
        self.read = self.string.read
        self.write = self.string.write
        self.getvalue = self.string.getvalue
        self.close = self.string.close
        self.readline = self.string.readline
        self.readlines = self.string.readlines
        self.tell = self.string.tell
        self.flush = self.string.flush

    def _backup(self, howmany):
        """
        Back the stream cursor up by `howmany` characters

        Required Arguments:
        howmany -- number of characters to back up

        """
        self.seek(-howmany,1)

    backup = _backup

    def isEnabled(self):
        """ 
        Is persistence enabled? 

        Returns: boolean indicating whether the persistence mechanism
            is currently enabled or not

        """
        return self.write is self.string.write

    def enable(self, offset=0):
        """ 
        Enable persistence 

        Keyword Arguments:
        offset -- the number of characters to shift the cursor
            before enabling persistence again

        """
        if offset: 
            self.seek(offset,1)
        persistlog.debug2('enable %s', offset)
        self.write = self.string.write
        self.backup = self._backup

    def disable(self, offset=0):
        """ 
        Disable persistence

        Keyword Arguments:
        offset -- the number of characters to shift the cursor
            before disabling persistence

        """
        if offset: 
            self.seek(offset,1)
        persistlog.debug2('disable %s', offset)
        self.write = self.devnull
        self.backup = self.devnull

    def devnull(self, *args, **kwargs):
        """ Functional equivalent to /dev/null """
        pass

    def getPosition(self, offset=0):
        """ 
        Get the current position of the stream 

        Keyword Arguments:
        offset -- number of characters to add to the current position
            before returning the result

        Returns: the current position of the stream cursor

        """
        return self.tell() + offset

    def getSource(self, start, end=None):
        """ 
        Get the source corresponding to the given object 

        Required Arguments:
        start -- either an integer starting position where reading 
            should start in the stream, or an instance of a macro.
            If a macro instance is given, no end position should
            be given; both beginning and ending positions will be
            extracted from the macro instance.

        Keyword Arguments:
        end -- position to quit reading

        Returns: string containing source from `start` to `end`, or 
            the string containing the source for the given macro instance

        """
        current = self.tell()
        if end is None:
            self.seek(start._source.start)
            value = self.read(start._source.end-start._source.start)
        else:
            self.seek(start)
            value = self.read(end-start)
        self.seek(current)
        return value


class TeX(object):
    """
    TeX Stream

    This class is the central TeX engine that does all of the 
    parsing, invoking of macros, etc.

    """

    persistent = Persistent()

    def __init__(self, s):
        if isinstance(s, basestring):
            self.string = StringIO(s)
            self.filename = None
        else:
            self.string = StringIO(s.read())
            self.filename = s.name

        self.context = Context

        # Mirror stream capabilities
        self.seek = self.string.seek
        self.read = self.string.read
        self.getvalue = self.string.getvalue
        self.close = self.string.close
        self.readline = self.string.readline
        self.readlines = self.string.readlines
        self.tell = self.string.tell
        self.flush = self.string.flush

    def disableLogging(cls):
        disableLogging()
    disableLogging = classmethod(disableLogging)

    def disablePersist(self, obj=None):
        """ 
        Temporarily disable the source persistence mechanism 

        Keyword Arguments:
        obj -- if given, the stream is reset to the point in the 
            stream where the macro instance `obj` began

        """
        if obj is None:
            offset = 0
        else:
            persistlog.debug3('disable position %s %s', obj._position, self.tell())
            offset = obj._position - self.tell()
        type(self).persistent.disable(offset)

    def enablePersist(self, obj=None):
        """ 
        Re-enable the persistence mechanism 

        Keyword Arguments:
        obj -- if given, the stream is reset to the point in the 
            stream where the macro instance `obj` began

        """
        if obj is None:
            offset = 0
        else:
            persistlog.debug3('enable position %s %s', obj._position, self.tell())
            offset = obj._position - self.tell()
        type(self).persistent.enable(offset)

    def getSource(self, begin, end):
        """ 
        Get the source from `begin` to `end` without modifying the stream 

        Required Arguments:
        begin -- starting position
        end -- ending position

        Returns:
        string containing LaTeX source

        """
        current = self.string.tell()
        self.string.seek(begin)
        content = self.string.read(end-begin) 
        self.string.seek(current)
        return content

    def getSourcePosition(self, offset=0):
        """ 
        Get the current position of the source stream 

        Keyword Arguments:
        offset -- number of characters to add to returned position

        Returns:
        position in the stream plus `offset`

        """
        return type(self).persistent.getPosition(offset)

    def peek(self):
        """ 
        Sneak a peek at the next character 

        Returns:
        next character in the stream

        """
        char = self.read(1) 
        self.seek(-1,1)
        return char

    def backup(self, howmany=1):
        """ 
        Back the stream cursor up by `howmany` characters

        Keyword Arguments:
        howmany -- number of characters to back up

        """
        self.seek(-howmany,1)
        type(self).persistent.backup(howmany)

    def next(self):
        """ 
        Iterator method - returns next character in stream 

        Returns:
        next character in the stream

        See Also:
        self.__iter__()

        """
        char = self.read(1) 
        if not char:
            raise StopIteration
        type(self).persistent.write(char)
        return char

    def __iter__(self):
        """
        Create iterator 

        Returns:
        iterator on the TeX stream

        See Also:
        self.next()

        """
        return self

    #
    # TeX specific methods
    #

    def removeWhitespace(self, newlines=False):
        """ 
        Remove all whitespace

        Keyword Arguments:
        newlines -- boolean indicating whether newlines should be
            absorbed as a whitespace character

        Returns:
        two-element tuple containing the total number of whitespace
        characters and the total number of newlines absorbed 

        """
        # Compile a list of all whitespace characters
        comment = self.context.categories[14]
        whitespace = self.context.categories[10]
        if newlines:
            whitespace += self.context.categories[5]

        total_whitespace = total_newlines = 0
        for char in self:
            if char == '\n':
                total_newlines += 1
            if char in comment:
                w,n = self.removeComment()
                total_whitespace += w
            elif char not in whitespace: 
                self.backup()    
                break
            total_whitespace += 1

        return total_whitespace, total_newlines

    def removeComment(self):
        """ 
        Remove the rest of the line and all trailing whitespace

        Returns:
        result of self.removeWhitespace() after removing the comment line

        See Also:
        self.removeWhitespace()

        """
        self.backup()
        start = self.tell()

        # We have to put the comment into the persisted source
        # in order to keep the streams in sync.
        type(self).persistent.write(self.readline())

        end = self.tell()

        return self.removeWhitespace()

    def normalize(self, tokens):
        """ 
        Combine consecutive strings and consecutive empty paragraphs 

        Required Arguments:
        tokens -- list of macro instances and strings

        Returns:
        list of tokens with strings and paragraphs normalized

        """
        # Locate the paragraph class
        par = type(self.context['par'])

        # Flatten and normalize using utility functions
        tokens = normalize(flatten(tokens))

        in_par = 0
        for i in range(len(tokens)):
            current = tokens[i]
            if isinstance(current, par):
                if in_par: 
                    tokens[i] = None
                in_par = 1 
            elif in_par and isinstance(current, basestring):
                tok = current.lstrip()
                if not tok:
                    tokens[i] = None
                else:
                    tokens[i] = tok
                    in_par = 0
            else:
                in_par = 0

        return [x for x in tokens if x is not None]

    def getUnexpandedArgument(self, spec=None, type=None, delim=',', raw=False):
        """
        Get an argument without expanding it into tokens

        See Also: self.getArgument()

        """
        self.context.push() 
        self.context.setCategoryCodesForDef()
        tokens = self.getArgument(spec=spec, type=type, delim=delim, raw=True)
        # I never quite figured out why, but this line has to be here
        self.persistent.read(1)
        if spec and len(spec) > 1:
            self.persistent.read(len(spec))
        self.context.pop()
        if tokens is not None:
            begin = self.context.categories[1][0]
            end = self.context.categories[2][0]
            tokens = normalize(flatten(tokens, begin+end))
            if tokens:
                if tokens[0] in self.context.categories[0]:
                    return tokens[0] + self.getWord()
                return tokens[0]
            else:
                return ''
        return None

    def getArgument(self, spec=None, type=None, delim=',', 
                          raw=False, expanded=True):
        """ 
        Get an argument 

        Optional Arguments:
        spec -- string containing information about the type of
            argument to get.  If it is 'None', the next token is
            returned.  If it is a two-character string, a grouping
            delimited by those two characters is returned (i.e. '[]').
            If it is a single-character string, the stream is checked
            to see if the next character is the one specified.  
            In all cases, if the specified argument is not found,
            'None' is returned.
        type -- data type to cast the argument to.  The currently 
            supported types are 'str', 'list', 'dict', 'int', and
            'float'.  This also includes subclasses of these types.
        delim -- item delimiter for list and dictionary types
        raw -- boolean indicating whether the raw token tree should
            be returned instead of a flattened list
        expanded -- boolean indicating whether the argument content
            should be expanded or just returned as an unexpanded 
            text string

        Returns:
        None -- if the argument wasn't found
        object of type `type` -- if `type` was specified
        raw tokens -- if `raw` is true
        TeXFragment -- for all other arguments

        """
        # Essentially get the argument as a verbatim string
        if not expanded:
            return self.getUnexpandedArgument(spec=spec, type=type, delim=delim)

        if type is not None and raw == True:
            raise ValueError, 'Datatype cannot be specified if raw=True'

        self.removeWhitespace(True)

        # Get a TeX token (i.e. {...})
        if spec is None:
            tok = self.getToken(raw=True) 
            if tok is not None and type is not None:
                return self.cast(tok, type, delim)
            elif tok is None:
                return None
            else:
                if raw:
                    return tok
                return TeXFragment(tokens2tree(self.normalize(tok)))

        # Get a single character argument
        elif len(spec) == 1:
            try: char = self.next()
            except StopIteration: return None
            if char == spec:
                return char
            else:
                self.backup()
                return None

        # Get an argument grouped by the given characters (e.g. [...], (...))
        elif len(spec) == 2:
            tok = self.getGroup(spec, raw=True)
            if tok is not None and type is not None:
                return self.cast(tok, type, delim)
            elif tok is None:
                return None
            else:
                if raw:
                    return tok
                return TeXFragment(tokens2tree(self.normalize(tok)))

        raise ValueError, 'Unrecognized specifier "%s"' % spec

    def cast(self, tokens, dtype, delim=','):
        """ 
        Cast the tokens to the appropriate type

        Required Arguments:
        tokens -- list of raw, unflattened and unnormalized tokens
        dtype -- reference to the requested datatype

        Optional Arguments:
        delim -- delimiter character for list and dictionary types

        Returns:
        object of the specified type

        """
        # Cast string, integer, and float types
        if issubclass(dtype, basestring) or issubclass(dtype, int) or \
           issubclass(dtype, float):
            arg = self.normalize(tokens)
            if len(arg) == 1:
                try: return dtype(arg[0])
                except: return arg[0]
            else: 
                return arg

        # Cast list types
        if issubclass(dtype, list) or issubclass(dtype, tuple):
            listarg = [[]]
            while tokens:
                current = tokens.pop(0)
                if current == delim:
                    listarg.append([])
                else:
                    listarg[-1].append(current) 
            listarg = [self.normalize(x) for x in listarg]
            # Strip leading whitespace from the first items.
            # If there is only one item, flatten it.
            for i in range(len(listarg)):
                if listarg[i] and hasattr(listarg[i][0], 'lstrip'):
                    try: listarg[i][0] = listarg[i][0].lstrip()
                    except: pass
                if len(listarg[i]) == 1:
                    listarg[i] = listarg[i][0]
            return dtype(listarg)

        # Cast dictionary types
        if issubclass(dtype, dict):
            dictarg = dtype()
            currentkey = []
            currentvalue = None
            while tokens:
                current = tokens.pop(0)

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
                    # Flatten key
                    currentkey = self.normalize(currentkey)
                    if len(currentkey) == 1 and \
                       hasattr(currentkey[0], 'lstrip'):
                        currentkey = currentkey[0].lstrip()
                    else:
                       currentkey = tuple(currentkey)

                    # Flatten value
                    if currentvalue is not None:
                        currentvalue = self.normalize(currentvalue)
                        if len(currentvalue) == 1:
                            currentvalue = currentvalue[0]

                    dictarg[currentkey] = currentvalue
                    currentkey = []
                    currentvalue = None

            return dictarg

        return self.normalize(tokens)

    def parse(self, raw=False):
        """ 
        Parse stream content until it is empty 

        Keyword Arguments:
        raw -- boolean indicating whether the output should be 
            returned as a normalized document fragment or 
            simply a list of tokens

        Returns:
        list of tokens -- if raw is True
        document fragment -- if raw is False

        """
        output = []

        # Continue to get tokens until the content is completely parsed
        try:
            while 1:
                try: 
                    output.append(self.getToken())
                except EndOfFile: 
                    break
        except:
           current = self.tell()
           self.seek(-min(current,80),1)
           log.error('%s', self.read(min(current,80)), exc_info=1)

        # Return raw tokens if requested
        if raw: return output

        # Build the document fragment
        output = TeXFragment(tokens2tree(self.normalize(output)))

        # If we have a document environment in the output, return
        # it by itself.  It's the only important thing.
        document = type(self.context['document'])
        doconly = [x for x in output if type(x) is document] 
        if doconly and len(doconly) == 1:
            return doconly[0]
        else:
            return output

#   def detokenizeArgument(self, tokens, params=None, categories=None):
#       """ 
#       Convert a tokenized argument back into a string 
#
#       Required Arguments:
#       tokens -- list of tokens as returned by self.getTokenizedArgument()
#     
#       Optional Arguments:
#       params -- list of tokenized arguments to be inserted into 
#           the macro parameter slots.  This list is zero-indexed,
#           not one-indexed like macro parameters.
#       categories -- alternate list of category codes to use
#
#       See Also: self.getTokenizedArgument()
#
#       """
#       if categories is None:
#           categories = self.context.categories
#       letters = categories[11]
#       try: escape = categories[0][0]
#       except IndexError: escape = None
#       try: param = categories[6][0]
#       except IndexError: param = None
#
#       if params is not None:
#           params = ['']+[self.detokenizeArgument(x, categories=categories) 
#                     for x in params]
#
#       previous = None
#       output = []
#       for item in iter(tokens):
#           # True tokens
#           if type(item) is Token:
#               try: output.append(categories[item.code][0])
#               except IndexError: output.append(item)
#
#           # Escape sequences
#           elif type(item) is EscapeSequence:
#               if escape is None:
#                   output.append(item)
#               else:
#                   output.append(escape)
#                   output.append(item[1:])
#
#           # Macro parameters
#           elif type(item) is MacroParameter: 
#               if params is None:
#                   if param is None:
#                       output.append(item)
#                   else:
#                       output.append(param)
#                       output.append(item[1:])
#               else:
#                   which = int(item[1:])
#                   if type(previous) is EscapeSequence:
#                      if previous[-1] in letters and \
#                         params[which] and params[which][0] in letters:
#                          output.append(' ')
#                   output.append(params[which])
#
#           # Character tokens
#           else:
#               output.append(item)
#
#           previous = item
#
#       return ''.join(output)

    def expandParams(self, definition, params=None):
        """
        Parse and substitute parameters into definition

        Required Arguments:
        definition -- string containing the definition to parse
        params -- parameters to substitute in place of arguments

        Returns:
        string contaning definition with parameters substituted

        """
        return str(self.getDefinitionArgument(params=params, definition=definition))

    def getDefinitionArgument(self, spec=None, params=None, definition=None):
        """ 
        Get argument as a series of tokens 

        Keyword Arguments:
        spec -- type of argument grouping to get (e.g. *, [...], (...))
        params -- list of parameters to substitute in place of 
            MacroParameter instances
        definition -- macro definition to parse

        Returns:
        argument of specified type

        Note:
        This whole definition expansion thing needs some work.  It
        doesn't work well when cat codes are switched around.

        """
        if definition is not None:
            self = type(self)(definition)

        output = []
        stack = 0
        begin_char = None
        end_char = None
        group_stack = 0

        self.removeWhitespace(True)

        # Check for groupings
        if spec is not None:

            # Single character argument
            if len(spec) == 1:
                try: next = self.next()
                except StopIteration: return
                if spec != next:
                    self.backup()
                    return None
                return next

            # Check for grouping arguments
            elif len(spec) == 2:
                try: next = self.next()
                except StopIteration: return
                if next != spec[0]:
                    self.backup()
                    return None
                begin_char = spec[0]
                end_char = spec[1]
                group_stack = 1

        self.context.push()

        first_char = True
        while True:

            try: token = self.next()
            except StopIteration: break
            code = self.context.whichCode(token)

            token = Token(token)
            token.code = code

            # Check for specified groupings
            if begin_char is not None:
                if token == begin_char:
                    group_stack += 1
                elif token == end_char:
                    group_stack -= 1
                    if group_stack == 0 and stack == 0:
                        break

            # Plain characters
            if code in [11, 12, 10, 5, 9, 15]:
                output.append(token) 

            # Begin group
            elif code == 1:
                stack += 1
                if not first_char:
                    output.append(token) 
                elif definition is not None:
                    output.append(token) 

            # End group
            elif code == 2:
                stack -= 1
                if stack:
                    output.append(token) 
                elif definition is not None:
                    output.append(token) 

            # Escope character
            elif code == 0:
                command = '%s%s' % (token, self.getWord())
                output.append(EscapeSequence(command))

            # Macro parameters
            elif code == 6:
                try: next = self.next()
                except StopIteration: next = None

                # Convert macro parameters to an object
                if next in string.digits:
                    if params is None:
                        output.append(MacroParameter(token+next))
                    else:
                        param = params[int(next)-1]
                        # Don't allow escape sequences before us to 
                        # run into parameters
                        try: previous = output[-1]
                        except IndexError: previous = None
                        if type(previous) is EscapeSequence and \
                           previous[-1] in string.letters and \
                           param and param[0] in string.letters:
                            output.append(' ') 
                        output.append(params[int(next)-1])

                # Let nested parameters pass through
                elif self.context.isCode(next,6):

                    # If we aren't doing parameter substitution, put
                    # the extra macro parameter charater back
                    if params is None:
                        token = ParameterToken(token)
                        output.append(token)

                    token = ParameterToken(next)
                    output.append(token)
                    while 1:
                        char = None
                        try: char = self.next()  
                        except StopIteration: break
                        if self.context.isCode(char,6):
                            token = ParameterToken(char)
                            output.append(token)
                        else:
                            break
                    if char is not None:
                        self.backup()

                # I don't know what this is, I'll just put it back
                else:
                    if next:
                        self.backup()
                    output.append(token)

            # Everything else
            else:
                output.append(token)

            first_char = False

            if definition is not None:
                pass
            elif stack == 0 and group_stack == 0:
                break

        self.context.pop()

        return ''.join(output)

    def getToken(self, absorb_space=False, raw=False):
        """ 
        Get the next token in the stream 

        Optional Arguments:
        absorb_space -- remove whitespace before searching for next token
        raw -- return raw, unflattened and unnormalized token if True

        Returns:
        the next TeX token in the stream

        """
        if absorb_space: self.removeWhitespace(newlines=True)

        try: token = self.next()
        except StopIteration: raise EndOfFile, 'End of content was reached'

        code = self.context.whichCode(token)

        # Plain characters
        if code in [11, 12]:
            return token 

        # Whitespace
        elif code == 10:
            whitespace, newlines = self.removeWhitespace(newlines=True)
            if newlines > 1:
                return self.invokeMacro('par')
            return ' '

        # Newlines
        elif code == 5:
            whitespace, newlines = self.removeWhitespace(newlines=True)
            if newlines > 0:
                return self.invokeMacro('par')
            return ' '

        # Begin group
        elif code == 1:
            self.context.groups.pushGrouping()
            tokens = []
            try:
                while 1:
                    tokens.append(self.getToken(raw=raw))
            except EndGroup: 
                tokens += self.context.groups.popGrouping(self)
            if raw: return tokens
            else: return self.normalize(tokens)

        # End group
        elif code == 2:
            raise EndGroup, 'An end grouping (%s) was reached' % token

        # Escope character
        elif code == 0:
            return self.invokeMacro()

        # Superscript
        elif code == 7:
            return self.invokeMacro('superscript')

        # Subscript
        elif code == 8:
            return self.invokeMacro('subscript')

        # Math shift
        elif code == 3:
            return self.invokeMacro('mathshift')

        # Alignment tab
        elif code == 4:
            return self.invokeMacro('alignmenttab')

        # Comment
        elif code == 14:
            self.removeComment()
            self.removeWhitespace()
            return self.getToken(raw=raw) 

        # Active character
        elif code == 13:
            return self.invokeMacro('textvisiblespace')

        # Macro parameter
        elif code == 6:
            return self.invokeMacro('macroparameter')

        elif code in [9,15]:
            pass

        raise ValueError, 'Did not recognize character "%s"' % token

    def invokeMacro(self, command=None):
        """ 
        Invoke a macro

        Keyword Arguments:
        command -- the name of the macro to invoke.  If this argument
            is missing, the name is read from the TeX stream.

        Returns:
        tokens as a result of invoking the macro 

        """
        # Get stream position information
        start = self.tell() - 1
        pstart = self.getSourcePosition(-1)

        # A name wasn't specified, so we need to parse it from the stream
        if command is None:
            command = self.getWord()
            # Short circuit \[ \] and \( \), they are the same as 
            # \begin{displaymath/math} and \end{displaymath/math}.  This
            # code works in conjunction with the [ ] and ( ) aliases
            # in Context and also in the `begin` and `end` classes. (yuck)
            if command in '[(': 
                command = 'begin'
                self.backup()
            elif command in '])': 
                command = 'end'
                self.backup()
            self.removeWhitespace(True)

        commandlog.debug('parsing command %s %s', command, start)

        # Get the Python macro class from the context for the given name
        command = self.context[command]

        # Set stream position information
        command._position = start
        command._source.stream = type(self).persistent
        command._source.start = pstart

        # Push the command's localized context onto the stack
        self.context.push(command)

        # Handle some of the document tree building related to sections
        tokens = []
        groups = self.context.groups
        if issection(command):
            sections = groups.sections
            sectionlog.debug('%s sections: %s' % (command.tagName, 
                                    [x.tagName for x in sections]))

            # No sections currently in the context, so we can 
            # just create a new grouping
            if not sections:
                sectionlog.debug('%s stack: %s' % (command.tagName, groups))
                groups.push(command)

            else:
                lower = [x for x in sections 
                                 if type(x).level >= type(command).level] 
                sectionlog.debug('%s lower sections: %s' % (command.tagName, 
                                                 [x.tagName for x in lower]))
                # There are no sections currently in the document
                # that are lower than us, hierarchically.
                if not lower:
                    groups.push(command)

                # There are sections in the document that are lower
                # (or equal) to us in the hierarchy.  They must be
                # popped from the context. 
                else:
                    sectionlog.debug('%s before: %s' % (command.tagName, groups))
                    tokens += groups.popLevel(type(command).level, self)
                    sectionlog.debug('%s after: %s' % (command.tagName, groups))
                    groups.push(command)
                
        # Environments should create new groupings
        elif isenv(command):
            groups.push(command)

        # Parse the command's arguments
        obj = command.parse(self)
        if hasattr(command, 'resolve'):
            command.resolve()

        # Removed the command's localized context
        self.context.pop()

        # Set stream position information
        command._source.end = self.getSourcePosition()

        # If tokens were popped off from lower level sections, append
        # this new macro onto those tokens.  Otherwise, just return
        # the new macro instance by itself.
        if tokens:
            tokens.append(obj)
            return tokens
        else:
            return obj

    def getWord(self):
        """ 
        Return a consecutive group of letters 

        Returns:
        string containing the following word in the stream

        """
        isCode = self.context.isCode
        try: word = self.next()
        except StopIteration: return ''
        if isCode(word, 11):
            word = [word]
            for char in self:
                if isCode(char, 11):
                    word.append(char)
                else:
                    self.backup()
                    break
            return ''.join(word)
        return word

#   def getSourceUntil(self, end, start=None):
#       current = self.tell()
#
#       if start is not None:
#           self.seek(start)
#
#       content = self.read()
#
#       # Find the first occurrence of the ending delimiter
#       position = content.find(end) + len(end)
#
#       # Get the content
#       if start is not None:
#           self.seek(start)
#       else:
#           self.seek(current)
#       content = self.read(position)
#       self.seek(current)
#       verbatimlog.debug('Source until %s %s', end, content)
#       return content
#
#   def getSourceUntilEndEnvironment(self, name, start=None):
#       end = '%send%s%s%s' % (self.context.categories[0][0], 
#                              self.context.categories[1][0],
#                              name,
#                              self.context.categories[2][0])
#       return self.getSourceUntil(end, start)

    def getVerbatim(self, end, strip_end=False):
        """
        Get verbatim text

        Required Arguments:
        end -- the string or list of strings that terminates 
            the verbatim text
        strip_end -- boolean indicating whether the string that
            terminated the verbatim text should be stripped
            from the returned string

        Returns:
        string containing text until `end`

        """
        if not (isinstance(end, list) or isinstance(end, tuple)):
            end = [end] 

        current = self.tell()
        content = self.read()

        # Find the first occurrence of the ending delimiter
        position = [content.find(x)+1 for x in end]
        try: minimum = min([x for x in position if x])
        except ValueError:
            self.seek(current,0)
            return ''
        index = position.index(minimum)

        # Reset the stream to where we started
        self.seek(current,0)

        # Get the verbatim content
        content = self.read(minimum-1)

        # Get rid of the ending delimiter
        if strip_end:
            self.read(len(end[index]))

        return content

    def getIfContent(self, which):
        """ 
        Get the content of an \\if block 

        Required Arguments:
        which -- boolean indicating which part of the \\if block
            to return.  True means to return the true portion; 
            False means to return the false portion.

        Returns:
        parsed tokens for the requested part of the \\if block

        """
        escape = self.context.categories[0][0]
        begin = re.sub(r'(\W)',r'\\\1',escape+'if')
        end = re.sub(r'(\W)',r'\\\1',escape+'fi')
        el = re.sub(r'(\W)',r'\\\1',escape+'else')
        orr = re.sub(r'(\W)',r'\\\1',escape+'or')

        # Which content to return 1 = false, 0 = true, any other
        # integer is for \ifcase.  I know this seems backwards, but
        # the output is put into a list and the true content comes
        # before the false content.
        if which:
            if type(which) is not int:
                which = 0
        else:
            which = 1

        current = self.tell()
        content = self.read()

        total = len(content)

        # Set up output array
        output = [[]]
        currentcontent = output[0]

        # Stack to keep track of nested \ifs
        stack = 1

        # Get all content before \fi
        splitter = re.compile(r'(%s|%s|%s)\b' % (end, el, orr))
        before, delim, after = splitter.split(content,1)
        currentcontent.append(before)
        inelse = False

        # Found \fi
        if re.match(end,delim):
            stack += len(re.findall(begin, before)) - 1
            if stack:
                currentcontent.append(delim)

        # Found \else or \or
        elif re.match(el,delim) or re.match(orr,delim):
            stack += len(re.findall(begin, before))
            if stack > 1:
                currentcontent.append(delim)
            else:
                output.append([])
                currentcontent = output[-1]

        content = after
        while stack:
            before, delim, after = splitter.split(content,1)
            currentcontent.append(before)

            # Found a \fi
            if re.match(end,delim):
                stack -= 1
                if stack == 0:
                    content = after 
                    break
                currentcontent.append(delim)

            # Found a top-level \else or \or
            elif stack == 1:
                output.append([])
                currentcontent = output[-1]

            # Found a nested \else
            else:
                currentcontent.append(delim)

            # Increment the stack to keep track of how many
            # levels of nested \ifs we have.
            if re.search(begin, before):
                stack += len(re.findall(begin, before))

            content = after 

        # Pick out the requested piece
        try: output = ''.join(output[which]).lstrip()
        except IndexError: output = ''

        # Put the stream back to the end of the \if block
        self.seek(current)
        self.seek(total-len(content),1)

        if output:
            return type(self)(output).parse(raw=True)
        else:
            return []

    def getGroup(self, group='[]', raw=False):
        """ 
        Get a series of tokens delimited by the given grouping chars 

        Keyword Arguments:
        group -- characters that delimit the requested group
        raw -- boolean indicating whether the output should be 
            an raw unnormalized list of tokens or a document fragment.

        Returns:
        None -- if the argument doesn't exist
        list of tokens or document fragment -- if the argument does exist

        """
        self.removeWhitespace(True)

        # Look for the beginning of the group
        try: char = self.next()
        except StopIteration: return
        if char != group[0]:
            self.backup()
            return 

        # Add an implicit grouping to the context
        self.context.groups.pushGrouping()

        tokens = []
        stack = 0
        self.removeWhitespace()
        while 1:
            char = self.getToken()
            if char == group[0]:
                stack += 1
            if not stack and char == group[1]:
                break
            if char == group[1]:
                stack -= 1
            tokens.append(char)

        # Pop the implicit context grouping
        tokens += self.context.groups.popGrouping(self)

        if raw: return tokens
        else: return self.normalize(tokens)

    def getSequence(self, code):
        """ 
        Get a string of characters from the given character code 

        Required Arguments:
        code -- numeric code of token to get the sequence of

        Returns:
        string containing characters of given code

        """
        isCode = self.context.isCode
        sequence = []
        for char in self:
            if isCode(char):
                sequence.append(char)
            else:
                self.backup()
                break
        return ''.join(sequence)

    def getSequenceWithTemplate(self, template):
        """ 
        Get a string of characters contained in template 

        Required Arguments:
        template -- characters to allow in the sequence

        Returns:
        string containing sequence of characters given in `template`

        """
        sequence = []
        for char in self:
            if char in template:
                sequence.append(char)
            else:
                self.backup()
                break
        return ''.join(sequence)

    def getFloat(self):
        """ 
        Get a decimal number from the stream 

        Returns:
        float parsed from the stream

        """
        multiplier = 1
        parts = []
        obj = self.getToken(absorb_space=True)
        if obj == '-':
            multiplier = -1
            obj = self.getToken(absorb_space=True)
        elif obj == '+':
            obj = self.getToken(absorb_space=True)

        if obj is None: return

        # Hard-coded number
        if obj in string.digits:
            parts.append(obj)
            parts.append(self.getSequenceWithTemplate(string.digits))
            try:
                if self.next() == '.':
                    parts.append('.')
                    if self.next() in string.digits:
                        self.backup()
                        parts.append(self.getSequenceWithTemplate(string.digits))
                    else:
                        self.backup()
                else:
                    self.backup()
            except StopIteration: pass

        # Command-sequence that holds a number
        else:
           parts.append('%s' % obj)

        return multiplier * float(''.join(parts))

    def getInteger(self):
        """ 
        Get an integer from the stream 

        Returns:
        integer parsed from the stream

        """
        multiplier = 1
        parts = []
        obj = self.getToken(absorb_space=True)
        if obj == '-':
            multiplier = -1
            obj = self.getToken(absorb_space=True)
        elif obj == '+':
            obj = self.getToken(absorb_space=True)

        if obj is None: return

        # Command-sequence that holds a number
        if ismacro(obj):
           parts.append('%s' % obj)
           if not parts[-1]:
               parts[-1] = '0'

        # Hard-coded number
        if str(obj) in string.digits:
            parts.append(obj)
            parts.append(self.getSequenceWithTemplate(string.digits))

        try: return multiplier * int(''.join([str(x) for x in parts]))
        except ValueError: return 0

    def getDimension(self):
        """ 
        Get a dimension from the stream 

        Returns:
        dimension parsed from the stream

        """ 
        self.removeWhitespace()
        parts = []
        obj = self.getToken(absorb_space=True)
        if ismacro(obj):
            return str(obj)
        elif obj == '-':
            parts.append('-')
            obj = self.getToken(absorb_space=True)
        elif obj == '+':
            obj = self.getToken(absorb_space=True)

        if obj is None: 
            return

        # Command-sequence that holds a number
        if ismacro(obj):
           parts.append('%s' % obj)
           if not parts[-1]:
               parts[-1] = '0pt'

        # Hard-coded number
        elif obj in string.digits:
            parts.append(obj)
            parts.append(self.getSequenceWithTemplate(string.digits))
            try:
                if self.next() == '.':
                    parts.append('.')
                    if self.next() in string.digits:
                        self.backup()
                        parts.append(self.getToken(absorb_space=True))
                        parts.append(self.getSequenceWithTemplate(string.digits))
                    else:
                        self.backup()
                else:
                    self.backup()
                self.removeWhitespace()
                parts.append(self.next())
                parts.append(self.next())
            except StopIteration: pass

        return str2dimen(''.join([str(x) for x in parts]))

    getLength = getDimension

    def getGlue(self):
        """ 
        Get a glue parameter from the stream 

        Returns:
        glue parsed from the stream 

        """ 
        glue = Glue(self.getDimension())

        # Get 'plus' if it exists
        position = self.tell()
        self.removeWhitespace()
        word = self.getWord()
        if word != 'plus':
            self.backup(self.tell()-position)
        else:
            glue.plus = self.getDimension()

        # Get 'minus' if it exists
        position = self.tell()
        self.removeWhitespace()
        word = self.getWord()
        if word != 'minus':
            self.backup(self.tell()-position)
        else:
            glue.minus = self.getDimension()

        return glue
