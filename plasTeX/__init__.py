#!/usr/bin/env python

import string, new, re
from Utils import *
from Token import *
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

    code = CC_EXPANDED # Special code for TeX to recognized expanded tokens
    mode = MODE_NONE

    def __init__(self, data=[]):
        Element.__init__(self, data)
        self.style = CSSStyles()
        self._position = None  # position in the input stream (internal use)
        #self._source = Source()
        self.argsource = ''

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

    def invoke(self, tex):
        tex.context.push(self)
        obj = self.parse(tex)
        tex.context.pop()
        return [obj]

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

        self.argsource = ''

        # Parse the arguments
        for arg in compiledargs:
            output, source = tex.getArgumentAndSource(**arg)
            self.argsource += source
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

        args = iter([x.strip() for x in re.split(r'([\'"]\w+[\'"]|\w+(?::\w+)*|\W|\s+)', type(self).args) if x is not None and x.strip()])

        groupings = {'[':'[]','(':'()','<':'<>','{':'{}'}

        macroargs = []
        argdict = {}
        for item in args:

            # Modifier argument
            if item in ['*','+','-']:
                if argdict:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, type(self).args)
                argdict.clear()
                macroargs.append(CompiledArgument('modifier', {'spec':item}))

            # Optional relations
            elif item in ['=']:
                if argdict:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, type(self).args)
                argdict.clear()
                macroargs.append(CompiledArgument('equals', {'spec':item}))

            # Beginning of group
            elif item in '[(<{':
                argdict['spec'] = groupings[item]

            # End of group
            elif item in '])>}':
                pass

            # Command sequence
            elif item == '\\':
                argdict['type'] = 'cs'

            # String argument
            elif item == '$':
                argdict['type'] = 'str'

            # List argument
            elif item == '@':
                argdict['type'] = 'list'

            # Dictionary argument
            elif item == '%':
                argdict['type'] = 'dict'

            # List delimiter
            elif item in [',',';','.']:
                argtype = argdict.get('type', None)
                if argtype in ['list', 'dict']:
                    argdict['delim'] = item
                else:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, type(self).args)

            # Argument name (and possibly type)
            elif item[0] in string.letters or item[0] in '\'"':
                parts = item.split(':')
                item = parts.pop(0)
                if item[0] in '\'"':
                    argdict['type'] = 'str'
                    item = item[1:]
                    if item[-1] in '\'"':
                        item = item[:-1]
                if parts: argdict['type'] = parts[0]
                # Arguments that are instance variables are always expanded
                if argdict.get('type') in ['cs','nox']:
                    argdict['expanded'] = False
                else:
                    argdict['expanded'] = True
                macroargs.append(CompiledArgument(item, argdict))
                argdict.clear()

            else:
                raise ValueError, 'Could not parse argument string "%s", reached unexpected "%s"' % (type(self).args, item)

        self.__compiled_arguments = macroargs
        return macroargs

    def nodeName(self):
        if self.texname: return self.texname
        return classname(self)
    nodeName = property(nodeName)

    def tagName(self):
        return self.nodeName
    tagName = property(tagName)

    def __repr__(self):
        if self.tagName == 'par':
            return '\n\n'
        if self.mode == MODE_BEGIN:
            return '\\begin{%s}%s' % (self.tagName, self.argsource)
        if self.mode == MODE_END:
            return '\\end{%s}' % self.tagName
        space = ' '
        if self.argsource:
            space = ''
        return '\\%s%s%s' % (self.tagName, self.argsource, space)


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
    
class UnrecognizedMacro(Macro):
    def invoke(self, tex):
       return [self]

class NewIf(Macro):
    """ Base class for all generated \\newifs """

    state = False

    def invoke(self, tex):
        return tex.getCase(type(self).state)

    def setState(cls, state):
        cls.state = state
    setState = classmethod(setState)

    def setTrue(cls):
        cls.state = True
    setTrue = classmethod(setTrue)

    def setFalse(cls):
        cls.state = False
    setFalse = classmethod(setFalse)

class IfTrue(Macro):
    """ Base class for all generated \\iftrues """
    def invoke(self, tex):
        type(self).ifclass.setTrue()
        return [self]

class IfFalse(Macro):
    """ Base class for all generated \\iffalses """
    def invoke(self, tex):
        type(self).ifclass.setFalse()
        return [self]

def expanddef(definition, params):
    # Walk through the definition and expand parameters
    output = []
    definition = iter(definition)
    for t in definition:
        # Expand parameters
        if t.code == CC_PARAMETER:
            for t in definition:
                # Double '#'
                if t.code == CC_PARAMETER:
                    output.append(t)
                else:
                    if params[int(t)] is not None:
                        output.extend(params[int(t)])
                break
        # Just append other tokens to the output
        else:
            output.append(t)
    return output

class NewCommand(Macro):
    """ Superclass for all \newcommand type commands """
    def invoke(self, tex):
        if self.mode == MODE_END:
            return tex.context['end'+self.tagName].invoke(tex)            

        if not self.definition:
            return []

        params = [None]

        # Get optional argument, if needed
        nargs = self.nargs
        if self.opt is not None:
            nargs -= 1
            params.append(tex.getArgument('[]', default=self.opt))

        # Get mandatory arguments
        for i in range(nargs):
            params.append(tex.getArgument())

        deflog.debug2('expanding %s %s', self.definition, params)

        return expanddef(self.definition, params)

class Definition(Macro):
    """ Superclass for all \\def-type commands """
    def invoke(self, tex):
        if not self.args: return self.definition

        argiter = iter(self.args)
        inparam = False
        params = [None]
        for a in argiter:

            # Beginning a new parameter
            if a.code == CC_PARAMETER:

                # Adjacent parameters, just get the next token
                if inparam:
                    params.append(tex.getArgument())

                # Get the parameter number
                for a in argiter:
                    # Numbered parameter
                    if a in string.digits:
                        inparam = True

                    # Handle #{ case here
                    elif t.code == CC_BGROUP:
                        param = []
                        for t in tex.itertokens():
                            if t.code == CC_BGROUP:
                                tex.pushtoken(t)
                            else:
                                param.append(t)
                        inparam = False
                        params.append(param)

                    else:
                        raise ValueError, \
                              'Invalid arg string: %s' % ''.join(self.args)
                    break

            # In a parameter, so get everything up to a token that matches `a`
            elif inparam:
                param = []
                for t in tex.itertokens():
                    if t == a:
                        break
                    else:
                        param.append(t)
                inparam = False
                params.append(param)

            # Not in a parameter, just make sure the token matches
            else:
                for t in tex.itertokens():
                    if t == a:
                        break
                    else:
                        raise ValueError, \
                            'Arguments don\'t match definition: %s %s' % (t, a)

        if inparam:
            params.append(tex.getArgument())

        deflog.debug2('expanding %s %s', self.definition, params)

        return expanddef(self.definition, params)


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

class TheCounter(Macro):
    """ Base class for counter formats """
    format = ''

class Dimen(float):

    units = ['pt','pc','in','bp','cm','mm','dd','cc','sp','ex','em']

    def __new__(cls, v):
        if isinstance(v, str) and v[-1] in string.letters:
            v = list(v)
            units = []
            while v and v[-1] in string.letters:
                units.insert(0, v.pop())
            v = float(''.join(v))
            units = ''.join(units) 
            if units == 'pt':
                v *= 65536
            elif units == 'pc':
                v *= 12 * 65536
            elif units == 'in':
                v *= 72.27 * 65536
            elif units == 'bp':
                v *= (72.27 * 65536) / 72
            elif units == 'cm':
                v *= (72.27 * 65536) / 2.54
            elif units == 'mm':
                v *= (72.27 * 65536) / 25.4
            elif units == 'dd':
                v *= (1238.0 * 65536) / 1157
            elif units == 'cc':
                v *= (1238.0 * 12 * 65536) / 1157
            elif units == 'sp':
                pass
            # Encode fil(ll)s by adding 1, 2, and 3 billion
            elif units == 'fil':
                if v < 0: v -= 1e9
                else: v += 1e9
            elif units == 'fill':
                if v < 0: v -= 2e9
                else: v += 2e9
            elif units == 'filll':
                if v < 0: v -= 3e9
                else: v += 3e9
            elif units == 'mu':
                pass
            # Just estimates, since I don't know the actual font size
            elif units == 'ex':
                v *= 5 * 65536
            elif units == 'em':
                v *= 11 * 65536
            else:
                raise ValueError, 'Unrecognized units: %s' % units
        return float.__new__(cls, v)

    def __repr__(self):
        sign = 1
        if self < 0:
            sign = -1
        if abs(self) >= 3e9:
            return repr(sign * (abs(self)-3e9)) + 'filll'
        if abs(self) >= 2e9:
            return repr(sign * (abs(self)-2e9)) + 'fill'
        if abs(self) >= 1e9:
            return repr(sign * (abs(self)-1e9)) + 'fil'
        return repr(float(self)) + 'sp'

    def pt(self): 
        return self / 65536
    point = pt = property(pt)

    def pc(self): 
        return self / (12 * 65536)
    pica = pc = property(pc)

    def _in(self): 
        return self / (72.27 * 65536)
    inch = _in = property(_in)

    def bp(self): 
        return self / ((72.27 * 65536) / 72)
    bigpoint = bp = property(bp)

    def cm(self): 
        return self / ((72.27 * 65536) / 2.54)
    centimeter = cm = property(cm)

    def mm(self): 
        return self / ((72.27 * 65536) / 25.4)
    millimeter = mm = property(mm)

    def dd(self): 
        return self / ((1238 * 65536) / 1157)
    didotpoint = dd = property(dd)

    def cc(self): 
        return self / ((1238 * 12 * 65536) / 1157)
    cicero = cc = property(cc)

    def sp(self): 
        return self
    scaledpoint = sp = property(sp)

    def ex(self): 
        return self / (5 * 65536)
    xheight = ex = property(ex)

    def em(self): 
        return self / (11 * 65536)
    mwidth = em = property(em)

    def fill(self):
        sign = 1
        if self < 0:
            sign = -1
        if abs(self) >= 3e9:
            return sign * (abs(self)-3e9)
        if abs(self) >= 2e9:
            return sign * (abs(self)-2e9)
        if abs(self) >= 1e9:
            return sign * (abs(self)-1e9)
        raise ValueError, 'This is not a fil(ll) dimension'
    fil = fill = filll = property(fill)

class Mudimen(Dimen):
    units = ['mu']

class Glue(Dimen):
    def __new__(cls, g, stretch=None, shrink=None):
        return Dimen.__new__(cls, g)
        
    def __init__(self, g, stretch=None, shrink=None):
        Dimen.__init__(self, g)
        self.stretch = stretch
        self.shrink = shrink

    def __repr__(self):
        s = [Dimen.__repr__(self)]
        if self.stretch is not None:
            s.append('plus')
            s.append(repr(self.stretch))
        if self.shrink is not None:
            s.append('minus')
            s.append(repr(self.shrink))
        return ' '.join(s)

class Muglue(Glue): 
    pass
