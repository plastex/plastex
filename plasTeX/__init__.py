#!/usr/bin/env python

import string, re
from Utils import *
from Tokenizer import Token, Node
from plasTeX.Logging import getLogger
from Renderer import RenderMixIn

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')
digestlog = getLogger('parse.digest')

class Argument(object):
    """ 
    Macro argument

    Argument strings in macros are compiled into Arguments
    once.  Then the compiled arguments can be used to get the 
    arguments thereafter.

    """
    def __init__(self, name, options={}):
        self.name = name
        self.source = ''
        self.options = options.copy()

    def __repr__(self):
        return '%s: %s' % (self.name, self.options)

    def __cmp__(self, other):
        c = cmp(self.name, other.name)
        if c: return c
        return cmp(self.options, other.options)


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

class Macro(Token, RenderMixIn):
    """
    Base class for all macros

    """
    MODE_NONE = 0
    MODE_BEGIN = 1
    MODE_END = 2

    macroName = None        # TeX macro name (instead of class name)
    macroMode = MODE_NONE   # begin, end, or none
    categories = None       # category codes local to this macro

    # Node variables
    level = Node.COMMAND_LEVEL
    nodeType = Node.ELEMENT_NODE
    nodeValue = None

    argsource = ''

    def source(self):
        return repr(self)
    source = property(source)

    def locals(self):
        """ Retrieve all macros local to this namespace """
        tself = type(self)
        if hasattr(tself, '__locals'):
            return tself.__locals
        mro = list(tself.__mro__)
        mro.reverse()
        locals = {}
        for cls in mro:
            for value in vars(cls).values():
                if ismacro(value):
                    locals[macroname(value)] = value
        tself.__locals = locals
        return locals
    locals = property(locals)

    def id(self):
        return id(self)
    id = property(id)

    def invoke(self, tex):
        # Just pop the context if this is a \end token
        if self.macroMode == Macro.MODE_END:
            tex.context.pop(self)
            return

        # If this is a \begin token or the element needs to be
        # closed automatically (i.e. \section, \item, etc.), just 
        # push the new context and return the instance.
        elif self.macroMode == Macro.MODE_BEGIN:
            tex.context.push(self)
            self.parse(tex)
            return

        # Push, parse, and pop.  The command doesn't need to stay on
        # the context stack.  We push an empty context so that the
        # `self' token doesn't get put into the output stream twice
        # (once here and once with the pop).
        tex.context.push(self)
        self.parse(tex)
        tex.context.pop(self)

    def tagName(self):
        t = type(self)
        if t.macroName is None:
            return t.__name__
        return t.macroName
    nodeName = tagName = property(tagName)

    def __repr__(self):
        if self.tagName == 'par':
            return '\n\n'

        # \begin environment
        # If self.childNodes is not none, print out the entire environment
        if self.macroMode == Macro.MODE_BEGIN:
            argsource = reprarguments(self)
            if not argsource: 
                argsource = ' '
            s = '\\begin{%s}%s' % (self.tagName, argsource)
            if self.childNodes is not None:
                s += '%s\\end{%s}' % (reprchildren(self), self.tagName)
            return s

        # \end environment
        if self.macroMode == Macro.MODE_END:
            return '\\end{%s}' % (self.tagName)

        argsource = reprarguments(self)
        if not argsource: 
            argsource = ' '
        s = '\\%s%s' % (self.tagName, argsource)

        # If self.childNodes is not none, print out the contents
        if self.childNodes is not None:
            s += reprchildren(self)
        return s

    def parse(self, tex): 
        """ 
        Parse the arguments defined in the `args` variable 

        Required Arguments:
        tex -- the TeX stream to parse from

        """
        if self.macroMode == Macro.MODE_END:
            return
        self.attributes = {}
        self.argsource = ''
        for arg in self.arguments:
            output, source = tex.getArgumentAndSource(**arg.options)
            self.argsource += source
            self.attributes[arg.name] = output

    def style(self):
        if not hasattr(self, '__style'):
            self.__style = CSSStyles()
        return self.__style
    style = property(style)

    def arguments(self):
        """ 
        Compile the argument string into function call arguments 

        Returns:
        arguments as compiled entities

        """
        t = type(self)

        if hasattr(t, '__arguments'):
            return t.__arguments

        if not(getattr(t, 'args', None)):
            t.__arguments = []
            return t.__arguments

        # Split the arguments into their primary components
        args = iter([x.strip() for x in re.split(r'(<=>|[\'"]\w+[\'"]|\w+(?::\w+)*|\W|\s+)', t.args) if x is not None and x.strip()])

        groupings = {'[':'[]','(':'()','<':'<>','{':'{}'}

        macroargs = []
        argdict = {}
        for item in args:

            # Modifier argument
            if item in '*+-':
                if argdict:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, t.args)
                argdict.clear()
                macroargs.append(Argument('*modifier*', {'spec':item}))

            # Optional equals
            elif item in '=':
                argdict.clear()
                macroargs.append(Argument('*equals*', {'spec':item}))

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

            # Definition arguments
            elif item == '#':
                argdict['type'] = 'args'

            # List delimiter
            elif item in ',;.':
                argtype = argdict.get('type', None)
                if argtype in ['list', 'dict']:
                    argdict['delim'] = item
                else:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, t.args)

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
                macroargs.append(Argument(item, argdict))
                argdict.clear()

            else:
                raise ValueError, 'Could not parse argument string "%s", reached unexpected "%s"' % (t.args, item)

        t.__arguments = macroargs
        return macroargs

    arguments = property(arguments)


class TeXFragment(list, Node, RenderMixIn):
    nodeName = tagName = '#document-fragment'
    nodeType = Node.DOCUMENT_FRAGMENT_NODE
 
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.childNodes = self

    def source(self):
        return u''.join([repr(x) for x in self])
    source = property(source)

class TeXDocument(TeXFragment):
    nodeName = tagName = '#document'
    nodeType = Node.DOCUMENT_NODE

    def __init__(self, *args, **kwargs):
        TeXFragment.__init__(self, *args, **kwargs)
        self.documentElement = self
        self.ownerDocument = self

    def preamble(self):
        output = []
        for item in self:
            if item.nodeName == 'document':
                break
            output.append(item)
        return TeXFragment(output)
    preamble = property(preamble)

class Command(Macro): 
    """ Base class for all Python-based LaTeX commands """

class Environment(Macro): 
    """ Base class for all Python-based LaTeX environments """
    level = Node.ENVIRONMENT_LEVEL

    def invoke(self, tex):
        if self.macroMode == Macro.MODE_END:
            tex.context.pop(self)
            return
        tex.context.push(self)
        self.parse(tex)

    def digest(self, tokens):
        if self.macroMode == Macro.MODE_END:
            return
        self.childNodes = []
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.nodeType == Node.ELEMENT_NODE:
                if item.macroMode == Macro.MODE_END and type(item) is type(self):
                    break
                item.digest(tokens)
            if item.contextDepth < self.contextDepth:
                tokens.push(item)
                break
            self.childNodes.append(item)
            item.parentNode = self
    
class StringMacro(Macro):
    """ 
    Convenience class for macros that are simply strings

    This class is used for simple macros that simply contain strings.

    Example::
        figurename = StringMacro('Figure')
        tablename = StringMacro('Table')

    """
    def invoke(self, tex): 
        return
                
class UnrecognizedMacro(Macro):
    """
    Base class for unrecognized macros

    When an unrecognized macro is requested, an instance of this 
    class is generated as a placeholder for the missing macro.

    """

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

class IfFalse(Macro):
    """ Base class for all generated \\iffalses """
    def invoke(self, tex):
        type(self).ifclass.setFalse()

def expanddef(definition, params):
    # Walk through the definition and expand parameters
    output = []
    definition = iter(definition)
    for t in definition:
        # Expand parameters
        if t.catcode == Token.CC_PARAMETER:
            for t in definition:
                # Double '#'
                if t.catcode == Token.CC_PARAMETER:
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
    """ Superclass for all \newcommand/\newenvironment type commands """
    nargs = 0
    opt = None
    definition = None

    def invoke(self, tex):
        if self.macroMode == Macro.MODE_END:
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
    args = None
    definition = None

    def invoke(self, tex):
        if not self.args: return self.definition

        argiter = iter(self.args)
        inparam = False
        params = [None]
        for a in argiter:

            # Beginning a new parameter
            if a.catcode == Token.CC_PARAMETER:

                # Adjacent parameters, just get the next token
                if inparam:
                    params.append(tex.getArgument())

                # Get the parameter number
                for a in argiter:
                    # Numbered parameter
                    if a in string.digits:
                        inparam = True

                    # Handle #{ case here
                    elif t.catcode == Token.CC_BGROUP:
                        param = []
                        for t in tex.itertokens():
                            if t.catcode == Token.CC_BGROUP:
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

    resetby = None
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
                         if x.resetby == type(self).__name__] 
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

class Dimen(float, Node):

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
            # Encode fil(ll)s by adding 2, 4, and 6 billion
            elif units == 'fil':
                if v < 0: v -= 2e9
                else: v += 2e9
            elif units == 'fill':
                if v < 0: v -= 4e9
                else: v += 4e9
            elif units == 'filll':
                if v < 0: v -= 6e9
                else: v += 6e9
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
        if abs(self) >= 6e9:
            return repr(sign * (abs(self)-6e9)) + 'filll'
        if abs(self) >= 4e9:
            return repr(sign * (abs(self)-4e9)) + 'fill'
        if abs(self) >= 2e9:
            return repr(sign * (abs(self)-2e9)) + 'fil'
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
        if abs(self) >= 6e9:
            return sign * (abs(self)-6e9)
        if abs(self) >= 4e9:
            return sign * (abs(self)-4e9)
        if abs(self) >= 2e9:
            return sign * (abs(self)-2e9)
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
