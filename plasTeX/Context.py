#!/usr/bin/env python

import sys, string, new, re, os
import plasTeX
from plasTeX import Macro, NewEnvironment, DOCUMENT, ENVIRONMENT, StringMacro
from plasTeX.Logging import getLogger
from Utils import *

# Set up loggers
log = getLogger()
grouplog = getLogger('context.groups')
stacklog = getLogger('context.stack')
macrolog = getLogger('context.macros')

# Default TeX category codes
CATEGORIES = [
   '\\',  # 0  - Escape character
   '{',   # 1  - Beginning of group
   '}',   # 2  - End of group
   '$',   # 3  - Math shift
   '&',   # 4  - Alignment tab
   '\n',  # 5  - End of line
   '#',   # 6  - Parameter
   '^',   # 7  - Superscript
   '_',   # 8  - Subscript
   '\000',# 9  - Ignored character
   ' \t', # 10 - Space
   string.letters + '@', # - Letter
   '',    # 12 - Other character - This isn't explicitly defined.  If it
          #                        isn't any of the other categories, then
          #                        it's an "other" character.
   '~',   # 13 - Active character
   '%',   # 14 - Comment character
   ''     # 15 - Invalid character
]

class _TokenGroup(object):
    """ Internal use only: for indicating the beginning of a new context """
    tagName = '{'

class GroupStack(list):
    """ 
    Manager for context groupings in LaTeX documents 

    Groupings are delimited by {...}, \\begin{foo}...\\end{foo}, and
    section headings in LaTeX documents.  This class manages those
    groupings and makes sure that the groups are both explicitly
    and implicitly terminated (e.g. \\bf is terminated by \\end{foo} in 
    \\begin{foo}\\bf ...\\end{foo}, sections also terminate open
    environments and subsections).

    Each time a new {, \\begin, or section heading is hit, a new 
    context grouping should be pushed.  When that grouping is finished,
    the context should be popped off.  Contexts can be popped off by
    supplying the initiating environment or {, a section level, or 
    the name of the macro that started the context grouping.

    """

    # Added to be consistent with pop terminology
    def push(self, *args, **kwargs): 
        return self.append(*args, **kwargs)

    def sections():
        doc = """ Return all section groupings """
        def fget(self):
            return [x for x in self 
                      if getattr(type(x), 'level', DOCUMENT) > DOCUMENT and 
                         getattr(type(x), 'level', ENVIRONMENT) < ENVIRONMENT]
        return locals()
    sections = property(**sections())

    def pushGrouping(self, env=None):
        """ 
        Push a new grouping onto the stack 

        Keyword Arguments:
        env -- the Environment instance that delimits the context group.
           If this isn't supplied, an anonymous grouping (i.e. {...})
           is assumed.

        """
        if env is None:
            self.append(_TokenGroup)
        else:
            self.append(env)

    def _parseEnd(self, env, tex):
        """ 
        Parse the end of a NewEnvironment 

        Required Arguments:
        env -- the NewEnvironment instance that needs to be parsed
        tex -- the TeX stream

        Returns: list of tokens in the end of the environment

        """
        output = []
        tokens = env.parseEnd(tex)
        if tokens is not None:
            output += tokens
        env._source.end = tex.getSourcePosition()
        return output

    def popGrouping(self, tex):
        """ 
        Pop until a TeX token group (i.e. {...}) is reached

        Required Arguments:
        tex -- the TeX stream instance corresponding to the source
            document.  This is needed in order to parse the ending
            of environments defined as NewEnvironments.

        Returns: list containing objects to insert into the output stream

        """
        grouplog.debug('Popping until grouping }')

        output = []
        while self:
           # Pop context grouping
           env = self.pop()

           # End condition reached (i.e. found {...} grouping), bail out
           if env is _TokenGroup:
               grouplog.debug('Popping grouping }')
               break

           # Get ending source position
           env._source.end = tex.getSourcePosition()

           # Parse end of NewEnvironments
           if isinstance(env, NewEnvironment):
               output += self._parseEnd(env, tex)

           # Anything else just gets appended to the output stream
           else:
               output.append(env)

        return output

    def popLevel(self, level, tex):
        """ 
        Pop off groupings until a token with the given level is reached 

        Required Arguments:
        level -- integer indicating the section level that ends 
           the context grouping
        tex -- the TeX stream instance corresponding to the source
            document.  This is needed in order to parse the ending
            of environments defined as NewEnvironments.

        Returns: list containing objects to insert into the output stream

        """
        assert isinstance(level, int), 'level must be an integer'
        grouplog.debug('Popping until level %s' % level)

        output = []
        while self:
           # Pop context grouping
           env = self.pop()

           # Just a token grouping (i.e. {...}).  Ignore it since
           # we are already in the process of ending a context that
           # implicitly ends all token groups.
           if env is _TokenGroup:
               continue

           # Get the current grouping's level
           if self: tokenlevel = getattr(type(self[-1]), 'level', sys.maxint)
           else: tokenlevel = sys.maxint

           grouplog.debug('Popping level %s (%s)' % (tokenlevel, env.tagName))

           # Get ending source position
           env._source.end = tex.getSourcePosition()

           # Parse end of NewEnvironments
           if isinstance(env, NewEnvironment):
               output += self._parseEnd(env, tex)

           # Anything else just gets appended to the output stream
           else:
               output.append(env)

           # Ending condition reached, bail out
           if tokenlevel < level:
               break

        return output

    def popName(self, name, tex):
        """ 
        Pop off groupings until a token with the given name is reached 

        Required Arguments:
        name -- name of the token that delimits the context grouping
        tex -- the TeX stream instance corresponding to the source
            document.  This is needed in order to parse the ending
            of environments defined as NewEnvironments.

        Returns: list containing objects to insert into the output stream

        """
        grouplog.debug('Popping until name %s' % name)

        output = []
        while self:
           # Pop context grouping
           env = self.pop()

           # Just a token grouping (i.e. {...}).  Ignore it since
           # we are already in the process of ending a context that
           # implicitly ends all token groups.
           if env is _TokenGroup:
               continue

           grouplog.debug('Popping name %s' % env.tagName)

           # Get ending source position
           env._source.end = tex.getSourcePosition()

           # Parse end of NewEnvironments
           if isinstance(env, NewEnvironment) and env.tagName != name:
               output += self._parseEnd(env, tex)

           # Anything else just gets appended to the output stream
           else:
               output.append(env)

           # Ending condition reached, bail out
           if env.tagName == name:
               break

        return output

    def popObject(self, obj, tex):
        """ 
        Pop off groupings including the given object 

        Required Arguments:
        obj -- the object that delimits the context grouping.  This is
            usually an Environment instance.
        tex -- the TeX stream instance corresponding to the source
            document.  This is needed in order to parse the ending
            of environments defined as NewEnvironments.

        Returns: list containing objects to insert into the output stream

        """
        grouplog.debug('Popping until object %s (%s)' % (obj.tagName, id(obj)))

        output = []
        while self:
           # Pop context grouping
           env = self.pop()

           # Just a token grouping (i.e. {...}).  Ignore it since
           # we are already in the process of ending a context that
           # implicitly ends all token groups.
           if env is _TokenGroup:
               continue

           grouplog.debug('Popping object %s (%s)' % (env.tagName, id(env)))

           # Get ending source position
           env._source.end = tex.getSourcePosition()

           # Parse end of NewEnvironments
           if isinstance(env, NewEnvironment):
               output += self._parseEnd(env, tex)

           # Anything else just gets appended to the output stream
           else:
               output.append(env)

           # Ending condition reached, bail out
           if env is obj:
               break

        return output

    def __repr__(self):
        """ Return string representation of objects that makeup the context """ 
        return str([x.tagName for x in self])

    def __str__(self):
        return repr(self)


class ContextItem(dict):
    """ Localized macros and category codes """
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.categories = None


class Context(object):
    """
    Object to handle macro contexts within a TeX document

    This class keeps track of macros (both global and local), labels,
    context groupings, category codes, etc.  The TeX parser uses this
    class to hold any and all information about the document currently
    being processed.  This class also contains methods to generate 
    new counters, ifs, dimensions, and other commands and macros.

    """

    def __init__(self):
        # Reference to renderer (default is empty)
        self.renderer = {}

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

        # Contex groupings
        self.groups = GroupStack() 

        # Macro dictionary
        self.macros = self

        # Aliases for non-alpha macros
        self.aliases = {
            ' ': 'textvisiblespace',
            '!': 'negative_thin_space',
            '\"': 'umlaut',
            '#': 'texthash',
            '$': 'textdollar',
            '%': 'textpercent',
            '&': 'textampersand',
            '\'': 'acute',
            '+': 'increment_tab',
            ',': 'thin_space',
            '-': 'hyphen',
            '.': 'dot',
            '/': 'italic_correction',
            ':': 'medium_space',
            ';': 'large_space',
            '<': 'tab_left',
            '=': 'macron',
            '>': 'tab_right',
            '@': 'extra_space',
            '\\': 'cr', 
            '^': 'circumflex',
            '_': 'underscore',
            '`': 'grave',
            '{': 'lbrace',
            '|': 'parallel',
            '}': 'rbrace',
            '~': 'tilde',
            # Special cases: these have corresponding code in TeX.py
            # and the `begin` and `end` classes.
            '(': 'math',
            ')': 'math',
            '[': 'displaymath',
            ']': 'displaymath',
        }

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

            # See if an alias exists
            if self.aliases.has_key(key) and c.has_key(self.aliases[key]):
                return c[self.aliases[key]]()

        # Didn't find it, so generate a new class
        log.warning('unrecognized macro %s', key)
        key = self.aliases.get(key, key)
        self[key] = newclass = new.classobj(key, (Macro,), {})
        return newclass()

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
        stacklog.debug('pushing %s %s', len(self.contexts), type(context))
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

        if context is not None:

            # If the new context is a macro, get it's category codes
            # and locally scoped macros
            if hasattr(type(context), 'categories') and \
               type(context).categories is not None:
                newcontext.categories = type(context).categories
 
            # If the context is not a dictionary, use dir to
            # get the localized macros.
            if not hasattr(context, 'items'):
                # Get all of the macros from the object
                ctype = type(context)
                context = {}
                for key in dir(ctype):
                    context[key] = getattr(ctype, key)

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

    def pop(self, index=-1):
        """ 
        Remove a context from the stack 

        Keyword Arguments:
        index -- index of context item to remove

        Returns: ContextItem instance removed from stack

        """
        c = self.contexts.pop(index)
        self.categories = self.contexts[-1].categories
        stacklog.debug('popping %s (%s)', len(self.contexts), index)
        return c

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
            if self.aliases.has_key(key) and d.has_key(self.aliases[key]):
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
                if key in self.aliases:
                    allkeys[self.aliases[key]] = 0
        return allkeys.keys()

    def __delitem__(self, key):
        """
        Deletes the first occurrence of the macro with name `key`

        Required Arguments:
        key -- the name of the macro to delete

        """
        for d in self.contexts:
            if d.has_key(key):
                del d[key]
        
    def isCode(self, char, code):
        """ 
        Determine if `char` is of category `code` 

        Required Arguments:
        char -- the character to check the category code of
        code -- the integer category code to test against

        Returns: boolean indicating if `char` is of code `code`

        """
        return char in self.categories[code]

    def whichCode(self, char):
        """ 
        Return the character code that `char` belongs to 

        Required Arguments:
        char -- character to determine the code of

        Returns: integer category code of the given character

        """
        c = self.categories
        if char in c[11]:
            return 11
        if char in c[10]:
            return 10
        if char in c[5]:
            return 5
        if char in c[1]:
            return 1
        if char in c[2]:
            return 2
        if char in c[0]:
            return 0
        if char in c[7]:
            return 7
        if char in c[8]:
            return 8
        if char in c[3]:
            return 3
        if char in c[4]:
            return 4
        if char in c[14]:
            return 14
        if char in c[13]:
            return 13
        if char in c[6]:
            return 6
        if char in c[9]:
            return 9
        if char in c[15]:
            return 15
        return 12

    def setCategoryCodesForDef(self):
        """ 
        Set category codes for macros that define new macros 

        """
        c = self.contexts[-1].categories = self.categories = self.categories[:]
        for i in [0, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 15]:
            c[i] = ''
        c[9] = '\000'
        c[10] = ' \t'
        
    def setCategoryCode(self, char, code):
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

    def newcounter(self, name, initial=0, reset_by=None, format=None):
        """ 
        Create a new counter 

        This method corresponds to LaTeX's \\newcounter command

        Required Arguments:
        name -- name of the counter.  The generate counter class will
            use this name.  Also, a new macro called 'the<name>' will
            also be generated for the counter format.

        Keyword Arguments:
        initial -- initial value for the counter
        reset_by -- the name of the counter that this counter is reset by
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
            {'reset_by':reset_by,'number':initial,'counters':self.counters})

        self.addGlobal(name, newclass)
        self.counters[name] = newclass()

        # Set up the default format
        if format is None:
            format = '%%(%s)s' % name
            if reset_by is not None: 
                format = '%%(the%s)s.%s' % (reset_by, format)

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

        assert isinstance(nargs, int), 'nargs must be an integer'
        assert isinstance(definition, list) or isinstance(definition, tuple), \
            'definition must be a list or tuple'
        assert len(definition) == 2, 'definition must have 2 elements'

        macrolog.debug('creating newenvironment %s', name)
        newclass = new.classobj(name, (plasTeX.NewEnvironment,),
                       {'nargs':nargs,'opt':opt,'definition':definition})

        self.addGlobal(name, newclass)

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


# Create single instance
Context = Context()

# Import all builtin macros
Context.importMacros(vars(plasTeX))
