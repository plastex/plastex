#!/usr/bin/env python

import string, new, re
from Utils import *
from plasTeX.DOM import *
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')

class CompiledArgument(dict):
    """ 
    Compiled macro argument

    Argument strings in macros are compiled into CompiledArguments
    once.  Then the compiled arguments can be used to get the 
    arguments thereafter.

    """
    def __init__(self, name, data={}):
        self.name = name
        self.update(data)
    def __repr__(self):
        return '%s: %s' % (self.name, dict.__repr__(self))
    def __cmp__(self, other):
        if self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return dict.__cmp__(self, other)

class CSSStyles(dict):
    """ CSS Style object """
    def inline(self):
        """ 
        Create an inline style representation

        Returns:
        string containing inline CSS

        """
        if not self:
            return None      
        return '; '.join(['%s:%s' % (x[0],x[1]) for x in self.items()])

class Source(object):
    """ 
    Class for retrieving the TeX source code of a macro 

    Each instance contains a reference to the expanded TeX source
    stream and two integers.  The integers correspond to the 
    beginning and ending positions in the source stream where
    the source for the current macro lies.

    """
    def __init__(self, stream=None):
        """
        Initialize Source

        Keyword Arguments:
        stream -- handle to stream that contains the TeX source

        """
        self.stream = stream
        self.start = None
        self.end = None

    def __str__(self):
        """ Retrieve the source from the TeX source stream """
        current = self.stream.tell()
        self.stream.seek(self.start)
        value = self.stream.read(self.end-self.start)
        self.stream.seek(current)
        return value

    def __repr__(self): return str(self)


class RenderMixIn(object):
    """
    MixIn class to make macros renderable

    """

    renderer = None

    def toXML(self):
        """ 
        Dump the object as XML 

        Returns:
        string in XML format

        """
        # Only the content of DocumentFragments get rendered
        if isinstance(self, DocumentFragment):
            s = []
            for value in self:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                s.append('%s' % value)
            return ''.join(s)

        # Remap name into valid XML tag name
        name = self.nodeName
        name = name.replace('@','-')

        modifier = re.search(r'(\W*)$', name).group(1)
        if modifier:
            name = re.sub(r'(\W*)$', r'', name)
            modifier = ' modifier="%s"' % xmlstr(modifier)

        if not name:
            name = 'unknown'

        source = ''
        if self._source.start is not None and self._source.end is not None:
            source = ' source="%s,%s"' % (self._source.start, self._source.end)

        # Bail out early if the element is empty
        if not(self.attributes) and not(self):
            return '<%s%s%s/>' % (name, modifier, source)

        s = ['<%s%s%s>\n' % (name, modifier, source)]
            
        # Render attributes
        if self.attributes:
#           s.append('<args>\n')
            for key, value in self.attributes.items():
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                else: 
                    value = xmlstr(value)
                if value is None:
                    s.append('    <plastex:arg name="%s"/>\n' % key)
                else:
                    s.append('    <plastex:arg name="%s">%s</plastex:arg>\n' % (key, value))
#           s.append('</args>\n')

        # Render content
        if self:
#           s.append('<content>')
            for value in self:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                else: 
                    value = xmlstr(value)
                s.append(value)
#           s.append('</content>\n')
        s.append('</%s>' % name)
        return ''.join(s)
        
    def render(self, renderer=None, file=None):
        """ 
        Render the macro 

        Keyword Arguments:
        renderer -- rendering callable to use instead of the
            one supplied by the macro itself
        file -- file write to

        Returns:
        rendered output -- if no file was specified
        nothing -- if a file was specified

        """
        # Get filename to use
        if file is None:
            file = type(self).context.renderer.filename(self)

        if file is not None:
            status.info(' [%s' % file)

        # If we have a renderer, use it
        if renderer is not None:
            output = renderer(self)

        # Use renderer associated with class
        elif type(self).renderer is not None:
            output = type(self).renderer(self)

        # No renderer, just make something up
        else:
            output = '%s' % self
#           output = ''.join([str(x) for x in self])
#           if type(self) is not TeXFragment:
#               name = re.sub(r'\W', 'W', self.tagName)
#               output = '<%s>%s</%s>' % (name, output, name)

        # Write to given file
        if file is not None:
            if hasattr(file, 'write'):
                file.write(output)
            else:
                open(file,'w').write(output)
            status.info(']')
            return ''

        # No files, just return the output
        else:
            return output

    def __str__(self):
        s = []
        for child in self:
            if isinstance(child, basestring):
                s.append(child)
            else:
                s.append(child.render())
        return ''.join(s)

    __repr__ = __str__


class Macro(Element, RenderMixIn):
    """
    Base class for all macros

    """
    level = COMMAND    # hierarchical level in the document
    categories = None  # category codes local to this macro
    counter = None     # counter corresponding to this macro
    section = False    # is this macro a section heading?
    texname = None     # TeX macro name (instead of class name)

    def __init__(self, data=[]):
        Element.__init__(self, data)
        self.style = CSSStyles()
        self._position = None  # position in the input stream (internal use)
        self._source = Source()

    def image(self):
        """ Render and return an image """
        return Macro.renderer.imager.newimage(self.source)
    image = property(image)

    def source(self):
        """ Return the LaTeX source for this macro instance """
        return str(self._source)
    source = property(source)

    def id(self):
        """ Unique ID """
        return id(self)

    def resolve(self):
        """ 
        Do post parsing operations (usually increment counters) 

        """
        context = type(self).context
        counter = type(self).counter
        if counter:
            context.currentlabel = self 
            context.counters[counter].refstepcounter()

    def parse(self, tex): 
        """ 
        Parse the arguments defined in the `args` variable 

        Required Arguments:
        tex -- the TeX stream to parse from

        Returns:
        tokens to be put into the output stream

        """
        # Compile argument string
        compiledargs = self.compileArgumentString()

        if not [x for x in compiledargs if x.name == 'modifier']:
            self.resolve()

        # Parse the arguments
        for arg in compiledargs:
            output = tex.getArgument(**arg)
            if arg.name == 'modifier':
                if output == None:
                    self.resolve() 
            if arg.name == 'self':
                if not isinstance(output, list):
                    output = [output]
                self[:] = output
            else:
                self.attributes[arg.name] = output

        return self

    def digest(self, tokens):
        """ 
        Absorb tokens in the stream that belong to us 

        The output stream, `tokens`, contains the entire LaTeX document
        as Macro objects and strings.  Environments are delimited
        by the same instance in the stream, so when `self` is found
        in the stream we know we have reached the end of the contents
        of the environment.

        Required Arguments:
        tokens -- iterator pointing to the remaining items in the
            output stream

        Returns: 
        self

        """
        # Commands don't digest
        if self.level is None:
            return self

        for item in tokens:
            # Found self again, we're done
            if item is self:
                break
            else:
                # Let children digest first
                if hasattr(item, 'digest'):
                    obj = item.digest(tokens)
                    if obj is not None:
                        if type(obj) is list:
                            self.extend(obj)
                        else:
                            self.append(obj)
                else:
                    self.append(item)

        return self

    def compileArgumentString(self):
        """ 
        Compile the argument string into function call arguments 

        Returns:
        arguments as compiled entities

        """
        if hasattr(self, '__compiled_arguments'):
            return self.__compiled_arguments

        if not hasattr(type(self), 'args'):
            self.__compiled_arguments = []
            return self.__compiled_arguments

        if not type(self).args: 
            self.__compiled_arguments = []
            return self.__compiled_arguments

        args = iter([x.strip() for x in re.split(r'(\W|\s+)', type(self).args) 
                                     if x.strip()])

        groupings = {'[':'[]','(':'()','<':'<>','{':'{}'}

        macroargs = []
        argdict = {}
        for item in args:

            # Plain argument
            if item == '$':
                if argdict.has_key('type'):
                    del argdict['type']

            # Modifier argument
            elif item in ['*','+','-']:
                if argdict:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, type(self).args)
                argdict.clear()
                macroargs.append(CompiledArgument('modifier', {'spec':item}))

            # Beginning of group
            elif item in ['[','(','<', '{']:
                argdict['spec'] = groupings[item]

            # End of group
            elif item in [']',')','>','}']:
                pass

            # List argument
            elif item == '@':
                argdict['type'] = list
                if argdict.has_key('raw'):
                    del argdict['raw']

            # Dictionary argument
            elif item == '%':
                argdict['type'] = dict
                if argdict.has_key('raw'):
                    del argdict['raw']

            # Unflattened 
            elif item == '^':
                argdict['raw'] = True
                if argdict.has_key('type'):
                    del argdict['type']

            # Numbers
            elif item == '#':
                argdict['type'] = int
                if argdict.has_key('raw'):
                    del argdict['raw']

            # Unexpanded argument
            elif item == '&':
                argdict['expanded'] = False

            # List delimiter
            elif item in [',',';','.']:
                argtype = argdict.get('type', None)
                if argtype is int and item == '.':
                    argdict['type'] = float 
                elif argtype in [list, dict]:
                    argdict['delim'] = item
                else:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, type(self).args)

            # Argument name
            elif item[0] in string.letters:
                macroargs.append(CompiledArgument(item, argdict))
                argdict.clear()

            else:
                raise ValueError, \
                    'Could not parse argument string "%s", reached unexpected "%s"' % (type(self).args, item)

        self.__compiled_arguments = macroargs
        return macroargs

    def nodeName(self):
        if self.texname: return self.texname
        return classname(self)
    nodeName = property(nodeName)

    def tagName(self):
        return self.nodeName
    tagName = property(tagName)


class TeXFragment(DocumentFragment, RenderMixIn):
    """ TeX document fragment """

    def __init__(self, *args, **kwargs):
        DocumentFragment.__init__(self, *args, **kwargs)
        self.style = CSSStyles()


class StringMacro(Macro):
    """ 
    Convenience class for macros that are simply strings

    This class is used for simple macros that simply contain strings.

    Example::
        figurename = StringMacro('Figure')
        tablename = StringMacro('Table')

    """
    def __init__(self, data=''):
        Macro.__init__(self, [data])
    def parse(self, tex): 
        return ''.join(self)
    def __call__(self):
        return self
                
class Command(Macro): 
    """ Base class for all Python-based LaTeX commands """

class Environment(Macro): 
    """ Base class for all Python-based LaTeX environments """
    level = ENVIRONMENT

class par(Macro):
    """ Paragraph """
    def parse(self, tex):
        status.dot()
        return Macro.parse(self, tex)

class mbox(Command):
    """ Math box """
    args = 'self'
    def parse(self, tex):
        shifted = 0
        if mathshift.inenv:
            shifted = 1
            mathshift.inenv.append(None)
        tokens = Command.parse(self, tex) 
        if shifted:
            mathshift.inenv.pop()
        return tokens

class mathshift(Macro):
    """ 
    The '$' character in TeX

    This macro detects whether this is a '$' or '$$' grouping.  If 
    it is the former, a 'math' environment is invoked.  If it is 
    the latter, a 'displaymath' environment is invoked.

    """
    inenv = []

    def parse(self, tex):
        """
        This gets a bit tricky because we need to keep track of both 
        our beginning and ending.  In addition, we need to make sure 
        that the image source isn't messed up.  We also have to take 
        into account \mbox{}es.

        """
        inenv = type(self).inenv
        math = tex.context['math']
        displaymath = tex.context['displaymath']

        # See if this is the end of the environment
        if inenv and inenv[-1] is not None:
            env = inenv.pop()
            if type(env) is type(displaymath):
                tex.next()
            return tex.context.groups.popObject(env, tex)

        # This must be the beginning of the environment
        if tex.peek() in tex.context.categories[3]:
            tex.next()
            self._source.stream = type(tex).persistent
            self._source.start = tex.getSourcePosition(-2)
            inenv.append(displaymath)
        else:
            self._source.stream = type(tex).persistent
            self._source.start = tex.getSourcePosition(-1)
            inenv.append(math)

        current = inenv[-1]
        mathshiftlog.debug('%s (%s): %s' % (current.tagName, id(current), 
                                            tex.context.groups))
        current._position = self._position
        current._source.stream = self._source.stream
        current._source.start = self._source.start
        current._source.end = self._source.end
        tex.context.groups.push(current)

        return current

class alignmenttab(Macro):
    """ The '&' character in TeX """

class textvisiblespace(Macro):
    """ The '~' character in TeX """

class superscript(Macro):
    """ The '^' character in TeX """
    args = 'self'

class subscript(Macro):
    """ The '_' character in TeX """
    args = 'self'

class macroparameter(Macro):
    """ Paramaters for macros (i.e. #1, #2, etc.) """
    def parse(self, tex):
        raise ValueError, 'Macro parameters should not be parsed'

class begin(Macro):
    """ Beginning of an environment """

    # Stack of all environments in the document
    envstack = []

    def parse(self, tex):
        """ Parse the \\begin{...} """
        # Get environment name, instantiate the proper environment, and
        # tell it to parse it's arguments.
        start = tex.tell() - 6 # Back up before the \begin
        name = tex.getArgument().pop(0).strip()

        # Special case for math environments
        if name in '[(':
            start += 5

        envlog.debug('begin %s', name)

        # Check for name aliases
        if tex.context.aliases.has_key(name):
            name = tex.context.aliases[name]

        # Add the current environment to the environment stack
        type(self).envstack.append(name)

        # Get the macro class for the given name
        env = tex.context[name]

        # Store stream position information
        env._source.stream = type(tex).persistent
        env._source.start = tex.getSourcePosition(start-tex.tell())
        env._position = start

        tex.context.pop()
        tex.context.push(env)
        tex.context.push(env)
        tex.context.push(env)
        tex.context.groups.push(env)

        # Parse the arguments
        output = env.parse(tex)

        if hasattr(env, 'resolve'):
            env.resolve()

        return output

class end(Macro):
    """ End of an environment """

    envstack = begin.envstack

    def parse(self, tex):
        """ Parse the \\end{...} """
        # Get the beginning of the environment from the stack and
        # put it into the stream again.  The document tree 
        # builder will take care of it.
        endenv = tex.tell() - 4
        name = tex.getArgument().pop(0).strip()

        # Special case for math environments
        if name in '])':
            endenv += 3

        envlog.debug('end %s', name)

        # Check for name aliases
        if tex.context.aliases.has_key(name):
            name = tex.context.aliases[name]

        # Get the macro class for the given name
        env = tex.context[name]

        # Store stream position information
        env._position = endenv

        # Handle NewEnvironments
        output = []
        if isinstance(env, NewEnvironment):
            output = env.parseEnd(tex)
            if output is None:
                output = []

        output += tex.context.groups.popName(env.tagName, tex)

        if isinstance(env, NewEnvironment):
            output.pop()

        # Make sure that our environment stack is correct
        beginname = type(self).envstack.pop()
        if name != beginname:
            log.warning('Expecting end of %s but got %s', beginname, name)

        tex.context.pop()
        tex.context.pop()

        return output


class _def(Macro):
    """
    TeX's \\def command

    """
    def parse(self, tex):

        name = str(tex.getDefinitionArgument().strip()[1:])

        # Get argument string
        args = []
        begingroup = tex.context.categories[1]
        try:
            while 1:
                char = tex.next()
                if char in begingroup:
                    tex.backup()
                    break
                else:
                    args.append(char) 
        except StopIteration: pass
        args = ''.join(args)

        # Parse definition from stream
        definition = str(tex.getDefinitionArgument())

        tex.context.pop()
        local = type(self).__name__ in ['def','edef']
        deflog.debug('def %s %s %s', name, args, definition)
        tex.context.newdef(name, args, definition, local=local)
        tex.context.push(self)

class x_def(_def): texname = 'def'
class edef(_def): pass
class xdef(_def): pass
class gdef(_def): pass

class NewIf(Macro):
    """ Base class for all generated \\newifs """

    state = False

    def parse(self, tex):
        tex.disablePersist(self)
        tokens = tex.getIfContent(type(self).state)
        tex.enablePersist()
        return tokens

    def setState(cls, state):
        cls.state = state
    setState = classmethod(setState)

    def setTrue(cls):
        cls.state = True
    setTrue = classmethod(setTrue)

    def setFalse(cls):
        cls.state = False
    setFalse = classmethod(setFalse)

class newif(Macro):
    """ \\newif """
    def parse(self, tex):
        name = tex.getDefinitionArgument().strip()[1:]
        tex.context.newif(name)

class IfTrue(Macro):
    """ Base class for all generated \\iftrues """
    def parse(self, tex):
        type(self).ifclass.setTrue()

class IfFalse(Macro):
    """ Base class for all generated \\iffalses """
    def parse(self, tex):
        type(self).ifclass.setFalse()

class _if(Macro):
    """ Test if character codes agree """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getArgument()
        b = tex.getArgument()
        tex.enablePersist()
        return tex.getIfContent(str(a)==str(b))

class x_if(_if): 
    """ \\if """
    texname = 'if'
        
class ifnum(_if):
    """ Compare two integers """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        relation = str(tex.getArgument()).strip()
        b = tex.getInteger()
        tex.enablePersist()
        if relation == '<':
            return tex.getIfContent(a < b)
        elif relation == '>':
            return tex.getIfContent(a > b)
        elif relation == '=':
            return tex.getIfContent(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifdim(_if):
    """ Compare two dimensions """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getDimension()
        relation = str(tex.getArgument()).strip()
        b = tex.getDimension()
        tex.enablePersist()
        if relation == '<':
            return tex.getIfContent(a < b)
        elif relation == '>':
            return tex.getIfContent(a > b)
        elif relation == '=':
            return tex.getIfContent(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifodd(_if):
    """ Test for odd integer """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(not(not(a % 2)))

class ifeven(_if):
    """ Test for even integer """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(not(a % 2))

class ifvmode(_if):
    """ Test for vertical mode """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(False)

class ifhmode(_if):
    """ Test for horizontal mode """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(True)

class ifmmode(_if):
    """ Test for math mode """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(False)

class ifinner(_if):
    """ Test for internal mode """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(False)

class ifcat(_if):
    """ Test if category codes agree """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.context.whichCode(str(tex.getArgument()))
        b = tex.context.whichCode(str(tex.getArgument()))
        tex.enablePersist()
        return tex.getIfContent(a == b)

class ifx(_if):
    """ Test if tokens agree """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getToken()
        b = tex.getToken()
        tex.enablePersist()
        return tex.getIfContent(a == b)

class ifvoid(_if):
    """ Test a box register """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(False)

class ifhbox(_if):
    """ Test a box register """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(False)

class ifvbox(_if):
    """ Test a box register """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(False)

class ifeof(_if):
    """ Test for end of file """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(False)

class iftrue(_if):
    """ Always true """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(True)

class iffalse(_if):
    """ Always false """
    def parse(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        return tex.getIfContent(False)

class ifcase(_if):
    """ Cases """
    def parse(self, tex):
        tex.disablePersist(self)
        a = tex.getInteger()
        tex.enablePersist()
        return tex.getIfContent(a)

class fi(Macro): pass
class x_or(Macro): texname = 'or'
class x_else(Macro): texname = 'else'


class let(Macro):
    """ \\let """
    def parse(self, tex):
        name = tex.getDefinitionArgument().strip()[1:]
        tex.getArgument('=')
        value = tex.getDefinitionArgument().strip()[1:]
        tex.context[name] = type(tex.context[value])


class Definition(Macro):
    """ Superclass for all \\def-type commands """
    def parse(self, tex):
        # Disable source persistence while parsing arguments
        tex.disablePersist(self)

        args = [x for x in re.split(r'(#+\d)', self.args) if x]
        params = []
        for arg in args:
            if arg.startswith('#'):
                params.append(tex.getDefinitionArgument())
            else:
                for char in arg:
                    next = tex.next()
                    if char == ' ' and next == ' ':
                        pass
                    elif char != next:
                        additional = []
                        while char != next:
                            additional.append(next)
                            next = tex.next()
                            if next == '\n':
                                raise ValueError, 'Use of %s does not match its definition' % self.tagName
                        if len(params) > 1:
                            params[-1] += ''.join(additional)
                        else:
                            params.append(''.join(additional))

        deflog.debug2('expanding %s %s', self.definition, params)

        definition = tex.expandParams(self.definition, params)

        # Re-enable source persistence
        tex.enablePersist()

        tokens = type(tex)(definition).parse(raw=True)

        return tokens


class newcommand(Macro):
    """ \\newcommand """
    def parse(self, tex):
        name = str(tex.getDefinitionArgument().strip()[1:])

        # Get number of arguments
        nargs = tex.getDefinitionArgument('[]')
        if nargs is None:
            nargs = 0
        else:
            nargs = int(nargs)

        # See if there is an optional argument
        opt = None
        if nargs:
            opt = tex.getDefinitionArgument('[]')

        # Get the macro definition
        definition = str(tex.getDefinitionArgument())
        if definition is None:
            definition = ''

        deflog.debug('command %s %s %s', name, nargs, definition)
        tex.context.newcommand(name, nargs, definition, opt=opt)

class renewcommand(newcommand): pass
class providecommand(newcommand): pass

class newenvironment(Macro):
    """ \\newenvironment """
    def parse(self, tex):
        name = str(tex.getDefinitionArgument().strip())

        # Get number of arguments
        nargs = tex.getDefinitionArgument('[]')
        if nargs is None:
            nargs = 0
        else:
            nargs = int(nargs)

        # See if there is an optional argument
        opt = None
        if nargs:
            opt = tex.getDefinitionArgument('[]')

        # Get the macro definition
        begin = str(tex.getDefinitionArgument())
        if begin is None:
            begin = ''
        end = str(tex.getDefinitionArgument())
        if end is None:
            end = ''
        definition = (begin,end)
        
        deflog.debug('environment %s %s %s', name, nargs, definition)
        tex.context.newenvironment(name, nargs, definition, opt=opt)


class NewCommand(Macro):
    """ Superclass for all \newcommand type commands """
    def parse(self, tex):
        params = []
        tex.disablePersist(self)

        # Get optional argument, if needed
        nargs = self.nargs
        if self.opt is not None:
            nargs -= 1
            opt = tex.getDefinitionArgument('[]')
            if opt is None:
                params.append(self.opt)
            else:
                params.append(opt)

        # Get mandatory arguments
        for i in range(nargs):
            params.append(tex.getDefinitionArgument())

        deflog.debug2('expanding %s %s', self.definition, params)
        definition = tex.expandParams(self.definition, params)

        tex.enablePersist()

        tokens = type(tex)(definition).parse(raw=True)

        return tokens


class NewEnvironment(NewCommand):
    """ Superclass for all \newenvironment type commands """
    def parse(self, tex):
        params = []
        tex.disablePersist(self)

        # Get optional argument, if needed
        nargs = self.nargs
        if self.opt is not None:
            nargs -= 1
            opt = tex.getDefinitionArgument('[]')
            if opt is None:
                params.append(self.opt)
            else:
                params.append(opt)

        # Get mandatory arguments
        for i in range(nargs):
            params.append(tex.getDefinitionArgument())

        deflog.debug2('expanding %s %s', self.definition, params)
        definition = tex.expandParams(self.definition[0], params)

        tex.enablePersist()

        tokens = type(tex)(definition).parse(raw=True)

        return tokens

    def parseEnd(self, tex):
        tex.disablePersist(self)
        tex.enablePersist()
        tokens = type(tex)(self.definition[1]).parse(raw=True)
        return tokens


class char(Macro):
    """ \\char """
    def parse(self, tex):
        try:
            char = tex.next()
            if char == "`":
                char = tex.next()
            if char == '\\':
                char = tex.next()
            char = tex.next() 
        except StopIteration: pass
        return char

class catcode(Macro):
    """ \\catcode """
    def parse(self, tex):
        char = tex.next()
        if char == "`":
            char = tex.next()
        if char == '\\':
            char = tex.next()
        if char == '^':
            return

        tex.getArgument('=')

        tex.removeWhitespace()

        nextchar = tex.peek()
        if nextchar in string.digits:
            number = tex.getInteger() 
        elif nextchar in tex.context.categories[0]:
            tex.next()
            m = tex.getWord()
            if m == 'active':
                number = 13
            else:
                raise ValueError, 'Unrecognized category "%s"' % m
        else:
            raise ValueError, 'Could not parse catcode'

        # Make sure we are changing the category code for the group below
        # where we are now
        tex.context.pop()
        tex.context.setCategoryCode(char,number)
        tex.context.push(self)


class Counter(Macro):
    """ Base class for all LaTeX counters """

    reset_by = None
    number = 0

    def __init__(self, number):
        type(self).number = int(number)

    def __int__(self):
        return type(self).number

    def __float__(self):
        return float(type(self).number)

    def __str__(self):
        return str(type(self).number)

    def __add__(self, other):
        return type(self)(int(self) + other)

    def __iadd__(self, other):
        type(self).number += other

    def __sub__(self, other):
        return type(self)(int(self) - other)

    def __isub__(self, other):
        type(self).number -= other

    def __mul__(self, other):
        return type(self)(int(self) * other)

    def __imul__(self, other):
        type(self).number *= other

    def __div__(self, other):
        return type(self)(int(self) / other)

    def __idiv__(self, other):
        type(self).number /= other

    def resetcounters(self):
        reset = [x for x in type(self).context.counters.values()
                         if x.reset_by == type(self).__name__] 
        for counter in reset:
            counter.setcounter(0)
            counter.resetcounters()

    def stepcounter(self):
        type(self).number += 1
        self.resetcounters()

    def setcounter(self, number):
        type(self).number = int(number)

    def addtocounter(self, number):
        type(self).number += int(number)

    def refstepcounter(self):
        self.stepcounter()

    def arabic(self):
        """ Return arabic representation """
        return str(int(self))

    def Roman(self):
        """ Return uppercase roman representation """
        roman = ""
        n, number = divmod(int(self), 1000)
        roman = "M"*n
        if number >= 900:
            roman = roman + "CM"
            number = number - 900
        while number >= 500:
            roman = roman + "D"
            number = number - 500
        if number >= 400:
            roman = roman + "CD"
            number = number - 400
        while number >= 100:
            roman = roman + "C"
            number = number - 100
        if number >= 90:
            roman = roman + "XC"
            number = number - 90
        while number >= 50:
            roman = roman + "L"
            number = number - 50
        if number >= 40:
            roman = roman + "XL"
            number = number - 40
        while number >= 10:
            roman = roman + "X"
            number = number - 10
        if number >= 9:
            roman = roman + "IX"
            number = number - 9
        while number >= 5:
            roman = roman + "V"
            number = number - 5
        if number >= 4:
            roman = roman + "IV"
            number = number - 4
        while number > 0:
            roman = roman + "I"
            number = number - 1
        return roman

    def roman(self):
        """ Return the lowercase roman representation """
        return self.Roman.lower()

    def Alph(self):
        """ Return the uppercase letter representation """
        return string.uppercase[int(self)-1]

    def alph(self):
        """ Return the lowercase letter representation """
        return string.lowercase[int(self)-1]

    def fnsymbol(self):
        """ Return the symbol representation """
        return '*'

class advance(Command):
    """ \\advance """
    def parse(self, tex):
        l = tex.getArgument()
        tex.getArgument('by')
        by = tex.getDimension()

class TheCounter(Macro):
    """ Base class for counter formats """
    format = ''

def str2dimen(s):
    """ Convert a string to a dimension """
    value = float(s.strip()[:-2])
    units = s.strip()[-2:]
    if units == 'pt':
        return Dimension(value)
    if units == 'pc':
        return Dimension(value*12)
    if units == 'in':
        return Dimension(value*72.27)
    if units == 'bp':
        return Dimension(value*(72.27/72))
    if units == 'cm':
        return Dimension(value*(72.27/2.54))
    if units == 'mm':
        return Dimension(value*(72.27/25.4))
    if units == 'dd':
        return Dimension(value*(1238/1157))
    if units == 'cc':
        return Dimension(value*(1238/1157)*12)
    if units == 'sp':
        return Dimension(value/65536)

class Dimension(float): 
    """ Base class for LaTeX dimensions """
    pass

class Glue(Dimension):
    def __init__(self, data=None):
       if data is not None:
           Dimension.__init__(self, data) 
       self.plus = Dimension()
       self.minus = Dimension()

class csname(Command):
    """ \\csname """
    def parse(self, tex):
        tex.disablePersist(self)
        escape = tex.context.categories[0][0]
        begin = tex.context.categories[1][0]
        end = tex.context.categories[2][0]
        name = tex.getVerbatim(escape+'endcsname', True).strip()
        name = name.replace(begin,'').replace(end,'')
        tex.enablePersist()
        return tex.invokeMacro(name)

class endcsname(Command): 
    """ \\endcsname """
    pass

class usepackage(Command):
    """ \\usepackage """
    args = '[ %options ] name'
    loaded = {}
    def parse(self, tex):
        attrs = self.attributes
        Command.parse(self, tex)
        try: 
            attrs['name'] = str(attrs['name']).strip()

            # See if it has already been loaded
            if type(self).loaded.has_key(attrs['name']):
                return

            try: 
                m = __import__(attrs['name'], globals(), locals())
                status.info(' ( %s ' % m.__file__)
                tex.context.importMacros(vars(m))
                type(self).loaded[attrs['name']] = attrs['options']
                status.info(' ) ')
                return

            except ImportError:
                log.warning('No Python version of %s was found' % attrs['name'])

            path = kpsewhich(attrs['name'])

            status.info(' ( %s.sty ' % attrs['name'])
            type(tex)(open(path)).parse(raw=True)
            type(self).loaded[self.name] = attrs['options']
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nError opening package "%s"' % attrs['name'])
            status.info(' ) ')

class documentclass(usepackage):
    """ \\documentclass """
    def parse(self, tex):
        usepackage.parse(self, tex)
        from plasTeX import packages
        tex.context.importMacros(vars(packages))

class RequirePackage(usepackage):
    """ \\RequirePackage """

class input(Command):
    """ \\input """
    args = 'name'
    def parse(self, tex):
        attrs = self.attributes
        Command.parse(self, tex)
        tokens = []
        try: 
            attrs['name'] = str(attrs['name']).strip()

            path = kpsewhich(attrs['name'])

            status.info(' ( %s.tex ' % attrs['name'])
            tokens = type(tex)(open(path)).parse(raw=True)
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nProblem opening file "%s"', attrs['name'])
            status.info(' ) ')
        return tokens

class include(input):
    """ \\include """

class x_ifnextchar(Command):
    texname = '@ifnextchar'
    def parse(self, tex):
        tex.removeWhitespace()
        ifchar = tex.next()
        truecontent = tex.getArgument(raw=True)
        falsecontent = tex.getArgument(raw=True)
        char = tex.next()
        tex.backup()
        if char == ifchar:
            return truecontent
        else:
            return falsecontent
