#!/usr/bin/env python

import new, plasTeX
from plasTeX import Macro, StringMacro, UnrecognizedMacro
from plasTeX.Logging import getLogger
from Tokenizer import Tokenizer, Token, DEFAULT_CATEGORIES, VERBATIM_CATEGORIES
from Utils import *

# Only export the Context class
__all__ = ['Context']

# Set up loggers
log = getLogger()
stacklog = getLogger('context.stack')
macrolog = getLogger('context.macros')


class ContextItem(dict):
    """ 
    Localized macro/category code stack element

    """

    def __init__(self, data={}):
        dict.__init__(self, data)
        self.categories = None
        self.obj = None
        self.parent = None
        self.owner = None
        self.name = '{}'
        if self.obj is not None:
            self.name = self.obj.nodeName

    def __getitem__(self, key):
        try: 
            return dict.__getitem__(self, key)
        except KeyError:
            if self.parent is not None:
                return self.parent[key]
            raise

    def get(self, key, default=None):
        try: return self[key]
        except KeyError: return default

    def has_key(self, key):
        if dict.has_key(self, key):
            return True
        if self.parent is not None:
            return self.parent.has_key(key)

    def keys(self):
        keys = {}
        for key in dict.keys(self):
            keys[key] = 0
        if self.parent is not None:
            for key in self.parent.keys():
                keys[key] = 0
        return keys.keys()

    def __str__(self):
        if self.parent is not None:
             return '%s -> %s' % (self.parent, self.name)
        return self.name


class Context(object):
    """
    Object to handle macro contexts within a TeX document

    This class keeps track of macros (both global and local), labels,
    context groupings, category codes, etc.  The TeX parser uses this
    class to hold any and all information about the document currently
    being processed.  This class also contains methods to generate 
    new counters, ifs, dimensions, and other commands and macros.

    """

    def __init__(self, tex=None):
        # Handle to the TeX instance that the context belongs to
        self.tex = tex

        # Stack of ContextItems
        self.contexts = []

        # Object that the current label points to
        self.currentlabel = None

        # Labeled objects
        self.labels = {}

        # Tokens aliased by \let
        self.lets = {}

        # Imported packages and their options
        self.packages = {}

        # Depth of the context stack
        self.depth = 0

        # Create a global namespace
        self.push()

    def loadBaseMacros(self):
        """ Import all builtin macros """
        from plasTeX import packages as _macros
        self.importMacros(vars(_macros))

        from plasTeX.packages import TeX as _macros
        self.importMacros(vars(_macros))

        from plasTeX.packages import LaTeX as _macros
        self.importMacros(vars(_macros))

    def __getitem__(self, key):
        """ 
        Look through the stack of macros and return the requested one 

        Required Arguments:
        key -- name of macro

        Returns: instance of requested macro

        """
        try: return self.top[key]()
        except KeyError: pass

        # Didn't find it, so generate a new class
        log.warning('unrecognized command/environment: %s', key)
        self[key] = newclass = new.classobj(str(key), (UnrecognizedMacro,), {})
        return newclass()

    def push(self, context=None):
        """ 
        Add a new context to the stack 

        This adds a new context grouping to the stack.  A context
        grouping includes both a set of localized macros and localized
        category codes.

        Keyword Arguments:
        context -- macro instance to use as the basis for a context
            grouping.  The local macros and category codes of this
            instance are used.  If this argument isn't supplied,
            an empty context is created.

        """
        if not self.contexts:
            context = ContextItem()
            context.categories = DEFAULT_CATEGORIES[:]
            self.contexts.append(context)

        else:
            name = '{}'
            if context is not None:
                name = context.nodeName 
            stacklog.debug('pushing %s onto %s', name, self.top)
            self.contexts.append(self.createContext(context))

        self.mapmethods()

    append = push

    def mapmethods(self):
        # Getter methods use the most local context
        self.top = top = self.contexts[-1]
        self.__getitem__ = top.__getitem__
        self.get = top.get
        self.keys = top.keys
        self.has_key = top.has_key
        self.categories = top.categories

        # Setter methods always use the global namespace
        globals = self.contexts[0]
        self.update = top.update
        self.__setitem__ = globals.__setitem__
#       self.__add__ = top.__add__
#       self.__radd__ = top.__radd__
#       self.__iadd__ = top.__iadd__

        # Set up inheritance attributes
        self.top.owner = self
        if len(self.contexts) > 1:
            self.top.parent = self.contexts[-2]

        self.depth = len(self.contexts)

    def createContext(self, obj=None):
        """
        Create the pieces of a new context (i.e. macros and category codes)

        Keyword Arguments:
        obj -- macro instance to use as the basis for a context
            grouping.  The local macros and category codes of this
            instance are used.  If this argument isn't supplied,
            an empty context is created.

        Returns: ContextItem instance 

        """
        newcontext = ContextItem()
        newcontext.categories = self.categories
        newcontext.obj = obj

        if obj is not None:

            # Get the local category codes and macros
            if obj.categories is not None:
                newcontext.categories = obj.categories

            newcontext.update(obj.locals)

        return newcontext

    def importMacros(self, context):
        """ 
        Import macros from given context into the global namespace

        Required Arguments:
        context -- dictionary of macros to import

        """
        for value in context.values():
            if ismacro(value):
                self[macroname(value)] = value
            elif isinstance(value, Context):
                self.importMacros(value)

    def pop(self, obj=None):
        """ 
        Remove a context from the stack 

        Keyword Arguments:
        index -- index of context item to remove

        Returns: ContextItem instance removed from stack

        """
        name = '{}'
        if obj is not None:
            name = obj.nodeName
        stacklog.debug('popping %s from %s', name, self.top)

        # Pop until we find a match, return a list of all of the
        # popped contexts (excluding `None's)
        o = c = None
        pushed = []
        while self.contexts:
            # Don't let them pop off the global namespace.  This should
            # should probably be an error since we have something 
            # incorrectly grouped.
            if len(self.contexts) == 1:
                stacklog.warning('%s%s is attempting to pop the global namespace.' % (name, self.tex.lineinfo))
                break

            # Pop the next context in the stack
            c = self.contexts.pop()
            o = c.obj

            # The same instance started and ended the context
            if obj is o:
                break

            # Found a matching {...}, break out
            if obj is None and o is None:
                stacklog.debug('implicitly pop {} from %s', self.top)
                break

            # Go to the next one, we don't have a match yet
            if obj is None or o is None:
                continue

            # Found the beginning of an environment with the same type.
            # We can finish popping contexts now.
            if type(obj) == type(o):
                stacklog.debug('implicitly pop %s from %s',o.nodeName,self.top)
                break

        self.mapmethods()

    def addGlobal(self, key, value):
        """ 
        Add a macro to the global context 

        Required Arguments:
        key -- name of macro to add
        value -- item to add to the global namespace.  If the item
            is a macro instance, it is simply added to the namespace.
            If it is a string, it is converted into a StringMacro
            instance before being added.

        """
        if isinstance(value, basestring):
            value = StringMacro(value)

        elif not ismacro(value):
            raise ValueError, \
                  '"%s" does not implement the macro interface' % key

        self.contexts[0][macroname(value)] = value

    __setitem__ = addGlobal

    def addLocal(self, key, value):
        """ 
        Add a macro to the local context 

        Required Arguments:
        key -- name of macro to add
        value -- item to add to the global namespace.  If the item
            is a macro instance, it is simply added to the namespace.
            If it is a string, it is converted into a StringMacro
            instance before being added.

        """
        if isinstance(value, basestring):
            value = StringMacro(value)

        elif not ismacro(value):
            raise ValueError, \
                  '"%s" does not implement the macro interface' % key

        self.contexts[-1][macroname(value)] = value

    def whichCode(self, char):
        """ 
        Return the character code that `char` belongs to 

        Required Arguments:
        char -- character to determine the code of

        Returns: integer category code of the given character

        """
        c = self.categories
        if char in c[Token.CC_LETTER]:
            return Token.CC_LETTER
        if char in c[Token.CC_SPACE]:
            return Token.CC_SPACE
        if char in c[Token.CC_EOL]:
            return Token.CC_EOL
        if char in c[Token.CC_BGROUP]:
            return Token.CC_BGROUP
        if char in c[Token.CC_EGROUP]:
            return Token.CC_EGROUP 
        if char in c[Token.CC_ESCAPE]:
            return Token.CC_ESCAPE 
        if char in c[Token.CC_SUPER]:
            return Token.CC_SUPER
        if char in c[Token.CC_SUB]:
            return Token.CC_SUB 
        if char in c[Token.CC_MATHSHIFT]:
            return Token.CC_MATHSHIFT
        if char in c[Token.CC_ALIGNMENT]:
            return Token.CC_ALIGNMENT 
        if char in c[Token.CC_COMMENT]:
            return Token.CC_COMMENT
        if char in c[Token.CC_ACTIVE]:
            return Token.CC_ACTIVE
        if char in c[Token.CC_PARAMETER]:
            return Token.CC_PARAMETER
        if char in c[Token.CC_IGNORED]:
            return Token.CC_IGNORED 
        if char in c[Token.CC_INVALID]:
            return Token.CC_INVALID
        return Token.CC_OTHER

    def catcode(self, char, code):
        """
        Set the category code for a particular character
 
        Required arguments:
        char -- the character to set the code of
        code -- the category code number to set `char` to

        """
        c = self.contexts[-1].categories = self.categories = self.categories[:]
        for i in range(0,16):
            c[i] = c[i].replace(char, '')
        # Don't insert if it's code 12.
        if code != 12:
            c[code] += char

    def setVerbatimCatcodes(self):
        """
        Set the category codes up for parsing verbatims

        This method turns the category codes for all characters to CC_OTHER

        """
        self.contexts[-1].categories = self.categories = VERBATIM_CATEGORIES[:]

    def newcounter(self, name, initial=0, resetby=None, format=None):
        """ 
        Create a new counter 

        This method corresponds to LaTeX's \\newcounter command

        Required Arguments:
        name -- name of the counter.  The generate counter class will
            use this name.  Also, a new macro called 'the<name>' will
            also be generated for the counter format.

        Keyword Arguments:
        initial -- initial value for the counter
        resetby -- the name of the counter that this counter is reset by
        format -- the presentation format for the counter 

        """
        name = str(name)
        # Counter already exists
        if self.has_key(name):
            macrolog.debug('counter %s already defined', name)
            return

        # Generate a new counter class
        macrolog.debug('creating counter %s', name)
        newclass = new.classobj(name, (plasTeX.Counter,), 
            {'resetby':resetby,'number':initial})

        self.addGlobal(name, newclass)

        # Set up the default format
        if format is None:
            format = '%%(%s)s' % name
            if resetby is not None: 
                format = '%%(the%s)s.%s' % (resetby, format)

        newclass = new.classobj('the'+name, (plasTeX.TheCounter,), 
                                {'format':format})

        self.addGlobal('the'+name, newclass)

    newcount = newcounter

    def newdimen(self, name, initial=0):
        """ NOT FINISHED """
        name = str(name)

        # Generate a new dimen class
        macrolog.debug('creating dimen %s', name)
        newclass = new.classobj(name, (plasTeX.Dimen,))

        self.addGlobal(name, newclass)

    def newskip(self, name, initial=0):
        """ NOT FINISHED """
        name = str(name)

        # Generate a new glue class
        macrolog.debug('creating dimen %s', name)
        newclass = new.classobj(name, (plasTeX.Glue,))

        self.addGlobal(name, newclass)

    def newif(self, name, initial=False):
        """ 
        Create a new \\if (and accompanying) commands 

        This method corresponds to TeX's \\newif command.

        Required Arguments:
        name -- name of the 'if' command.  This name should always
            start with the letters 'if'.

        Keyword Arguments:
        initial -- initial value of the 'if' command

        """        
        name = str(name)
        # \if already exists
        if self.has_key(name):
            macrolog.debug('if %s already defined', name)
            return

        # Generate new 'if' class
        macrolog.debug('creating if %s', name)
        ifclass = new.classobj(name, (plasTeX.NewIf,), {'state':initial})
        self.addGlobal(name, ifclass)

        # Create \iftrue macro
        truename = name[2:]+'true'
        newclass = new.classobj(truename, (plasTeX.IfTrue,), 
                                {'ifclass':ifclass})
        self.addGlobal(truename, newclass)

        # Create \iffalse macro
        falsename = name[2:]+'false'
        newclass = new.classobj(falsename, (plasTeX.IfFalse,), 
                                {'ifclass':ifclass})
        self.addGlobal(falsename, newclass)

    def newcommand(self, name, nargs=0, definition=None, opt=None):
        """ 
        Create a \\newcommand 

        Required Arguments:
        name -- name of the macro to create
        nargs -- integer number of arguments that the macro has
        definition -- string containing the LaTeX definition
        opt -- string containing the LaTeX code to use in the 
            optional argument

        Examples::
            c.newcommand('bold', 1, r'\\textbf{#1}')
            c.newcommand('foo', 2, r'{\\bf #1#2}', opt='myprefix')

        """
        name = str(name)
        # Macro already exists
        if self.has_key(name):
            macrolog.debug('newcommand %s already defined', name)
            return

        if nargs is None:
            nargs = 0
        assert isinstance(nargs, int), 'nargs must be an integer'

        if isinstance(definition, basestring):
            definition = [x for x in Tokenizer(definition, self)]

        if isinstance(opt, basestring):
            opt = [x for x in Tokenizer(opt, self)]

        macrolog.debug('creating newcommand %s', name)
        newclass = new.classobj(name, (plasTeX.NewCommand,),
                       {'nargs':nargs,'opt':opt,'definition':definition})

        self.addGlobal(name, newclass)

    def newenvironment(self, name, nargs=0, definition=None, opt=None):
        """ 
        Create a \\newenvironment 

        Required Arguments:
        name -- name of the macro to create
        nargs -- integer number of arguments that the macro has
        definition -- two-element tuple containing the LaTeX definition.
            Each element should be a string.  The first element 
            corresponds to the beginning of the environment, and the
            second element is the end of the environment.
        opt -- string containing the LaTeX code to use in the 
            optional argument

        Examples::
            c.newenvironment('mylist', 0, (r'\\begin{itemize}', r'\\end{itemize}'))

        """
        name = str(name)
        # Macro already exists
        if self.has_key(name):
            macrolog.debug('newenvironment %s already defined', name)
            return

        if nargs is None:
            nargs = 0
        assert isinstance(nargs, int), 'nargs must be an integer'

        if definition is not None:
            assert isinstance(definition, (tuple,list)), \
                'definition must be a list or tuple'
            assert len(definition) == 2, 'definition must have 2 elements'

            if isinstance(definition[0], basestring):
                definition[0] = [x for x in Tokenizer(definition[0], self)]
            if isinstance(definition[1], basestring):
                definition[1] = [x for x in Tokenizer(definition[1], self)]

        if isinstance(opt, basestring):
            opt = tex.tokenize(opt)

        macrolog.debug('creating newenvironment %s', name)

        # Begin portion
        newclass = new.classobj(name, (plasTeX.NewCommand,),
                       {'nargs':nargs,'opt':opt,'definition':definition[0]})
        self.addGlobal(name, newclass)

        # End portion
        newclass = new.classobj('end'+name, (plasTeX.NewCommand,),
                       {'nargs':0,'opt':None,'definition':definition[1]})
        self.addGlobal('end' + name, newclass)

    def newdef(self, name, args=None, definition=None, local=True):
        """ 
        Create a \def 

        Required Arguments:
        name -- name of the macro to create
        args -- string containing the TeX argument profile
        definition -- string containing the LaTeX definition
      
        Keyword Arguments:
        local -- indicates whether this macro is local or global

        Examples::
            c.newdef('bold', '#1', '{\\bf #1}')
            c.newdef('put', '(#1,#2)#3', '\\dostuff{#1}{#2}{#3}')

        """
        name = str(name)
        # Macro already exists
        if self.has_key(name):
            macrolog.debug('def %s already defined', name)
            return

        if isinstance(definition, basestring):
            definition = [x for x in Tokenizer(definition, self)]

        macrolog.debug('creating def %s', name)
        newclass = new.classobj(name, (plasTeX.Definition,),
                       {'args':args,'definition':definition})

        if local:
            self.addLocal(name, newclass)
        else:
            self.addGlobal(name, newclass)

    def let(self, dest, source):
        """
        Create a \let

        Required Arguments:
        dest -- the command sequence to create
        source -- the token to set the command sequence equivalent to

        Examples::
            c.let('bgroup', BeginGroup('{'))

        """
        self.lets[dest] = source
