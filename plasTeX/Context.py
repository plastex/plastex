#!/usr/bin/env python

import sys, string, new, re, os
import plasTeX
from plasTeX import Macro, DOCUMENT, ENVIRONMENT, StringMacro, UnrecognizedMacro
from plasTeX.Logging import getLogger
from Utils import *
from Categories import *

# Set up loggers
log = getLogger()
stacklog = getLogger('context.stack')
macrolog = getLogger('context.macros')


class ContextItem(dict):
    """ Localized macros and category codes """
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.categories = None
        self.obj = None


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
        # Reference to renderer (default is empty)
        self.renderer = {}

        # Handle to the TeX instance that the context belongs to
        self.tex = tex

        # Stack of ContextItems
        c = ContextItem()
        c.categories = CATEGORIES[:]
        self.contexts = [c]
        self.categories = c.categories

        # Object that the current label points to
        self.currentlabel = None

        # Counter macros
        self.counters = {}

        # Length macros
        self.lengths = {}

        # LaTeX boxes
        self.boxes = {}

        # Labeled objects
        self.labels = {}

        # Tokens aliased by \let
        self.lets = {}

        # Macro dictionary
        self.macros = self

        # Import all builtin macros
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
        key = str(key)
        # Look for the request macro in the stack (locals first)
        for i in range(len(self.contexts)-1, -1, -1):
            c = self.contexts[i]
            if c.has_key(key):
                return c[key]()

        # Didn't find it, so generate a new class
        log.warning('unrecognized macro %s', key)
        self[key] = newclass = new.classobj(key, (UnrecognizedMacro,), {})
        return newclass()

    def contextNames(self):
        c = []
        for item in self.contexts:
            if item.obj is None:
                c.append('{}')
            else:
                c.append(item.obj.nodeName)
        return '->'.join(c)

    def __delitem__(self, key):
        """ 
        Delete first occurrence of a macro with name `key` 

        Required Arguments:
        key -- name of macro to delete

        """
        for i in range(len(self.contexts)-1, -1, -1):
            c = self.contexts[i]
            if c.has_key(key):
                del c[key] 
                break

    def __iadd__(self, other):
        """ Absorb macros from another context into the globals """
        macros = self.contexts[0]
        for key, value in other.items():
            if ismacro(value):
                macros[key] = value
        return self

    update = __add__ = __radd__ = __iadd__

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
        name = '{}'
        if context is not None:
            name = context.nodeName 
        stacklog.debug('pushing %s onto %s', name, self.contextNames())
        self.contexts.append(self.createContext(context))
        self.categories = self.contexts[-1].categories

    append = push

    def createContext(self, context=None):
        """
        Create the pieces of a new context (i.e. macros and category codes)

        Keyword Arguments:
        context -- macro instance to use as the basis for a context
            grouping.  The local macros and category codes of this
            instance are used.  If this argument isn't supplied,
            an empty context is created.

        Returns: ContextItem instance 

        """
        newcontext = ContextItem()
        newcontext.categories = self.categories
        newcontext.obj = context

        if context is not None:

            # If the new context is a macro, get it's category codes
            # and locally scoped macros
            cat = getattr(type(context), 'categories', None)
            if cat is not None:
                newcontext.categories = cat
 
            # If the context is not a dictionary, use dir to
            # get the localized macros.
            if not hasattr(context, 'items'):
                mro = list(type(context).__mro__)
                mro.reverse()
                context = {}
                for item in mro:
                    context.update(vars(item))

            # Add the locally scoped macros to the current context
            attr = 'texname'
            for key, value in context.items():
                if hasattr(value, attr):
                    if value.texname:
                        key = value.texname
                    newcontext[key] = value

        return newcontext

    def insert(self, index, context=None):
        """ 
        Insert a new context into the stack 

        Required Arguments:
        index -- position to put the new context.  If this number 
            is equal to or greater than the length of the context 
            stack, the new context is simply appended to the 
            current stack.
        context -- the context to insert

        """
        if index >= len(self.contexts):
            self.append(context)
        else:
            stacklog.debug('inserting %s %s (%s)', 
                           (len(self.contexts), type(context), index))
            self.contexts.insert(index, self.createContext(context))

    def importMacros(self, context):
        """ 
        Import macros from given context into the global namespace

        Required Arguments:
        context -- dictionary of macros to import

        """
        for key, value in context.items():
            if ismacro(value):
                self[key] = value

    def applyRenderer(self, renderer):
        """ Apply rendering methods to top level macros """
        self.renderer = renderer
        macros = self.contexts[0]
        default = renderer.get('_default_', None)
        for key, value in macros.items():
            value.renderer = renderer.get(key, default)
        Macro.renderer = renderer

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
        stacklog.debug('popping %s from %s', name, self.contextNames())

        # Pop until we find a match, return a list of all of the
        # popped contexts (excluding `None's)
        o = c = None
        while self.contexts:
            # Don't let them pop off the global namespace.  This should
            # should probably be an error since we have something 
            # incorrectly grouped.
            if len(self.contexts) == 1:
                stacklog.warning('Attempting to pop the global namespace.')
                break

            # Pop the next context in the stack
            c = self.contexts.pop()
            o = c.obj

            # Found a matching {...}, break out
            if obj is None and o is None:
                stacklog.debug('implicitly pop {} from %s', self.contextNames())
                break

            # Go to the next one, we don't have a match yet
            if obj is None or o is None:
               continue

            # Found the beginning of an environment with the same name.
            if obj.nodeName == o.nodeName:
                stacklog.debug('implicitly pop %s from %s', o.nodeName, 
                               self.contextNames())
                break

        self.categories = self.contexts[-1].categories

        return o

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

        value.context = self

        if value.texname:
            key = value.texname

        self.contexts[0][key] = value

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

        value.context = self

        if value.texname:
            key = value.texname

        self.contexts[-1][key] = value

    def has_key(self, key):
        """
        Does the name exist in any current context?

        Required Arguments:
        key -- the macro name to look for

        Returns: boolean indicating whether or not the macro was found

        """
        for d in self.contexts:
            if d.has_key(key):
                return True
        return False

    def keys(self):
        """
        Return the names of all macros in the entire context

        Returns: list of macro names

        """
        allkeys = {}
        for d in self.contexts:
            for key in d.keys():
                allkeys[key] = 0
        return allkeys.keys()

    def __delitem__(self, key):
        """
        Deletes the all occurrences of the macro with name `key`

        Required Arguments:
        key -- the name of the macro to delete

        """
        for d in self.contexts:
            if d.has_key(key):
                del d[key]
        
    def whichCode(self, char):
        """ 
        Return the character code that `char` belongs to 

        Required Arguments:
        char -- character to determine the code of

        Returns: integer category code of the given character

        """
        c = self.categories
        if char in c[CC_LETTER]:
            return CC_LETTER
        if char in c[CC_SPACE]:
            return CC_SPACE
        if char in c[CC_EOL]:
            return CC_EOL
        if char in c[CC_BGROUP]:
            return CC_BGROUP
        if char in c[CC_EGROUP]:
            return CC_EGROUP 
        if char in c[CC_ESCAPE]:
            return CC_ESCAPE 
        if char in c[CC_SUPER]:
            return CC_SUPER
        if char in c[CC_SUB]:
            return CC_SUB 
        if char in c[CC_MATHSHIFT]:
            return CC_MATHSHIFT
        if char in c[CC_ALIGNMENT]:
            return CC_ALIGNMENT 
        if char in c[CC_COMMENT]:
            return CC_COMMENT
        if char in c[CC_ACTIVE]:
            return CC_ACTIVE
        if char in c[CC_PARAMETER]:
            return CC_PARAMETER
        if char in c[CC_IGNORED]:
            return CC_IGNORED 
        if char in c[CC_INVALID]:
            return CC_INVALID
        return CC_OTHER

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
            {'resetby':resetby,'number':initial,'counters':self.counters})

        self.addGlobal(name, newclass)
        self.counters[name] = newclass()

        # Set up the default format
        if format is None:
            format = '%%(%s)s' % name
            if resetby is not None: 
                format = '%%(the%s)s.%s' % (resetby, format)

        newclass = new.classobj('the'+name, (plasTeX.TheCounter,), 
                                {'format':format})

        self.addGlobal('the'+name, newclass)

    newcount = newcounter

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

    def newcommand(self, name, nargs, definition, opt=None):
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

        macrolog.debug('creating newcommand %s', name)
        newclass = new.classobj(name, (plasTeX.NewCommand,),
                       {'nargs':nargs,'opt':opt,'definition':definition})

        self.addGlobal(name, newclass)

    def newenvironment(self, name, nargs, definition, opt=None):
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
        assert isinstance(definition, (tuple,list)), \
            'definition must be a list or tuple'
        assert len(definition) == 2, 'definition must have 2 elements'

        macrolog.debug('creating newenvironment %s', name)

        # Begin portion
        newclass = new.classobj(name, (plasTeX.NewCommand,),
                       {'nargs':nargs,'opt':opt,'definition':definition[0]})
        self.addGlobal(name, newclass)

        # End portion
        newclass = new.classobj('end'+name, (plasTeX.NewCommand,),
                       {'nargs':0,'opt':None,'definition':definition[1]})
        self.addGlobal('end' + name, newclass)

    def newdef(self, name, args, definition, local=True):
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

        macrolog.debug('creating def %s', name)
        newclass = new.classobj(name, (plasTeX.Definition,),
                       {'args':args,'definition':definition})

        if local:
            self.addLocal(name, newclass)
        else:
            self.addGlobal(name, newclass)

    def let(self, dest, source):
        self.lets[dest] = source
