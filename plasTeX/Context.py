#!/usr/bin/env python

import new, os, ConfigParser, re, time, codecs
import plasTeX
from plasTeX import ismacro, macroName
from plasTeX.DOM import Node
from plasTeX.Logging import getLogger
from Tokenizer import Tokenizer, Token, DEFAULT_CATEGORIES, VERBATIM_CATEGORIES

# Only export the Context singleton
__all__ = ['Context']

# Set up loggers
log = getLogger()
status = getLogger('status')
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

    @property
    def name(self):
        if self.obj is not None:
            return self.obj.nodeName
        return '{}'

    def __getitem__(self, key):
        try: 
            return dict.__getitem__(self, key)
        except KeyError:
            if self.parent is not None and self.parent is not self:
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

    __contains__ = has_key

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


class Counters(dict):
    def __getitem__(self, name):
        try: 
            c = dict.__getitem__(self, name)
        except KeyError:
#           log.warning('No counter "%s" exists.  Creating one.' % name)
            c = self[name] = plasTeX.Counter(self.context, name)
        return c


class LanguageParser(object):
    """ Parser for language commands """

    def __init__(self, output={}):
        self.data = output
        self.language = None
        self.term = None

    def parse(self, files, encoding='UTF-8'):
        from xml.parsers import expat
        if isinstance(files, basestring):
            files = [files]
        for file in files:
            if not os.path.isfile(file):
                continue
            self.parser = expat.ParserCreate('UTF-8')
            self.parser.StartElementHandler = self.startElement
            self.parser.EndElementHandler = self.endElement
            self.parser.CharacterDataHandler = self.charData
            self.parser.Parse(codecs.open(file, 'r', encoding).read().encode('UTF-8'))
        self.mergeLanguages()
        return self.data

    def mergeLanguages(self):
        # Merge language keys from the major language section, into
        # the minor language section
        for key, value in self.data.items():
            if '-' in key:
                major, minor = key.split('-',1)
                if major in self.data:
                    majordict = self.data[major]
                    for mkey, mvalue in majordict.items():
                        if mkey not in value:
                            value[mkey] = mvalue

    def startElement(self, name, attrs):
        if name == 'terms':
            self.term = None
            if self.data.get(attrs['lang']):
                self.language = self.data[attrs['lang']] 
            else:
                self.language = self.data[attrs['lang']] = {}
            if 'babel' in attrs:
                self.data[attrs['babel']] = self.language
        elif name == 'term':
            self.term = attrs['name']
            self.language[self.term] = u''
            
    def endElement(self, name):
        if name == 'term':
            self.term = None
            
    def charData(self, data):
        if self.term:
            self.language[self.term] += data


class Context(object):
    """
    Object to handle macro contexts within a TeX document

    This class keeps track of macros (both global and local), labels,
    context groupings, category codes, etc.  The TeX parser uses this
    class to hold any and all information about the document currently
    being processed.  This class also contains methods to generate 
    new counters, ifs, dimensions, and other commands and macros.

    """

    def globals(self):
        return self.contexts[0]

    def __init__(self, load=False):
        # Stack of ContextItems
        self.contexts = []

        # Object that the current label points to
        self.currentlabel = None

        # Labeled objects
        self.labels = {}
        self.persistentLabels = {}

        # Unresolved refs
        self.refs = {}

        # LaTeX counters
        self.counters = Counters()
        self.counters.context = self

        # Tokens aliased by \let
        self.lets = {}

        # Imported packages and their options
        self.packages = {}

        # Output files
        self.writes = {}

        # Depth of the context stack
        self.depth = 0

        # Holds the current environment name stack
        self._currenvir = []

        # Holds the terms for various languages
        self.languages = {}
        self.terms = {}
        self.currentLanguage = ''

        # Create a global namespace
        self.push()

        self.warnOnUnrecognized = True

        if load:
            self.loadBaseMacros()

    def currenvir():
        def fget(self):
            if self._currenvir:
                return self._currenvir[-1]
            return
        def fset(self, value):
            if value is None:
                self._currenvir.pop()
            else:
                self._currenvir.append(value)
        def fdel(self):
            self._currenvir.pop()
        return locals()
    currenvir = property(**currenvir())

    def persist(self, filename, rtype='none'):
        """
        Persist cross-document information for labeled nodes

        Required Arguments:
        filename -- the name of the file with the shelved data
 
        Keyword Arguments:
        rtype -- the key in the shelved data to look under.  This is generally
            the name of the renderer used since the information for each
            renderer may be different.

        """
        import pickle
        if os.path.exists(filename):
            try:
                d = pickle.load(open(filename,'rb'))
                if rtype not in d:
                    d[rtype] = {}
            except:
                os.remove(filename)
                d = {rtype:{}}
        else:
            d = {rtype:{}}
        data = d[rtype]
        for key, value in self.persistentLabels.items():
            data[key] = value.persist()
        try:
            pickle.dump(d, open(filename,'wb'))
        except Exception, msg:
            log.warning('Could not save auxiliary information. (%s)' % msg)

    def restore(self, filename, rtype='none'):
        """
        Restore cross-document information for labeled nodes

        Required Arguments:
        filename -- the name of the file with the shelved data
 
        Keyword Arguments:
        rtype -- the key in the shelved data to look under.  This is generally
            the name of the renderer used since the information for each
            renderer may be different.

        """
        import pickle
        if not os.path.exists(filename):
            return
        try:
            d = pickle.load(open(filename,'rb'))
            try: data = d[rtype]
            except KeyError: return
            wou = self.warnOnUnrecognized
            self.warnOnUnrecognized = False
            for key, value in data.items():
                n = self[value.get('macroName','Macro')]()
                n.restore(value)
                self.labels[key] = n
            self.warnOnUnrecognized = wou
        except Exception, msg:
            log.warning('Could not load auxiliary information. (%s)' % msg)

    @property
    def isMathMode(self):
        """ Are we in math mode or not? """
        for i in range(len(self.contexts)-1, -1, -1):
            obj = self.contexts[i].obj
            if obj is not None and obj.mathMode is not None:
                return obj.mathMode
        return False

    def loadBaseMacros(self):
        """ Import all builtin macros """
        from plasTeX import Base
        self.importMacros(vars(Base))

    def loadLanguage(self, lang, document):
        """
        Load a localized version of macros for a particular language

        Required Arguments:
        lang -- the name of the language file to load

        """
        if not self.languages:
            files = document.config['document']['lang-terms'].split(os.pathsep)
            files.append(os.path.join(os.path.dirname(__file__), 'i18n.xml'))
            LanguageParser(self.languages).parse(reversed(files))

        if lang in self.languages:
            self.currentLanguage = lang
            self.newcommand('languagename', definition=lang)
            self.terms = self.languages[lang]
            for key, value in self.languages[lang].items():
                if key == 'today':
                    self.newcommand(key, definition=self._strftime(value))                
                else:
                    self.newcommand('%sname' % key, definition=value)
        else:
            log.warning('Could not load language "%s", american will be used instead' % lang)

    def _strftime(self, fmt):
        if '%f' in fmt or '%e' in fmt:
            day = time.strftime('%d')
            suffix = 'th'
            if day.endswith('1'):
                suffix = 'st'
            elif day.endswith('2'):
                suffix = 'nd'
            elif day.endswith('3'):
                suffix = 'rd'
            day = str(int(day))
            return time.strftime(fmt.replace('%f', day+suffix).replace('%e', day))
        return time.strftime(fmt)

    def loadINIPackage(self, inifile):
        """ 
        Load INI file containing macro definitions

        Arguments:
        inifile -- filename of INI formatted file

        """
        ini = ConfigParser.RawConfigParser()
        if not isinstance(inifile, (list,tuple)):
            inifile = [inifile]
        for f in inifile:
            ini.read(f)
            macros = {}
            for section in ini.sections():
                try: baseclass = self[section]
                except KeyError:
                    log.warning('Could not find macro %s' % section)
                    continue
                for name in ini.options(section):
                    value = ini.get(section,name)
                    m = re.match(r'^unicode\(\s*(?:(\'|\")(?P<string>.+)(?:\1)|(?P<number>\d+))\s*\)$',value)
                    if m:
                        data = m.groupdict()
                        if data['number'] is not None:
                            value = unichr(int(data['number']))
                        else:
                            value = unicode(data['string'])
                        macros[name] = new.classobj(name, (baseclass,), 
                                                    {'unicode': value})
                        continue 
                    macros[name] = new.classobj(name, (baseclass,), 
                                                {'args': value})
            self.importMacros(macros)

    def loadPackage(self, tex, file, options={}):
        """
        Load a Python or LaTeX package

        A Python version of the package is searched for first,
        if one cannot be found then a LaTeX version of the package
        is searched for.

        Required Arguments:
        tex -- the instance of the TeX engine to use for parsing
            the LaTeX file, if needed.
        file -- the name of the file to load

        Keyword Arguments:
        options -- the options given on the macro to pass to the package

        Returns:
        boolean indicating whether or not the package loaded successfully

        """
        module = os.path.splitext(file)[0]

        # See if it has already been loaded
        if self.packages.has_key(module):
            return True

        packagesini = os.path.join(os.path.dirname(plasTeX.Packages.__file__), 
                                   os.path.basename(module)+'.ini')

        try: 
            # Try to import a Python package by that name
            m = __import__(module, globals(), locals())
            status.info(' ( %s ' % m.__file__)
            if hasattr(m, 'ProcessOptions'):
                m.ProcessOptions(options or {}, tex.ownerDocument)
            self.importMacros(vars(m))
            moduleini = os.path.splitext(m.__file__)[0]+'.ini'
            self.loadINIPackage([packagesini, moduleini])
            self.packages[module] = options
            status.info(' ) ')
            return True

        except ImportError, msg:
            # No Python module
            if 'No module' in str(msg):
                pass
                # Failed to load Python package
#               log.warning('No Python version of %s was found' % file)
            # Error while importing
            else:
                raise

        result = tex.loadPackage(file, options)
        try:
            moduleini = os.path.join(os.path.dirname(tex.kpsewhich(file)),
                                     os.path.basename(module)+'.ini')
            self.loadINIPackage([packagesini, moduleini])
        except OSError: pass
        return result
   

    def label(self, label, node=None):
        """ 
        Set a label to the current labelable object

        Required Arguments:
        label -- string that contains the label

        Keyword Arguments:
        node -- a node to apply the label to rather than the currently
            labelable object

        See Also:
        self.ref()

        """
        label = label.strip()
        if not label:
            return

        if node is None:
            node = self.currentlabel

        if node is not None:
            self.persistentLabels[label] = self.labels[label] = node
            node.id = label

        #print label, ''.join(self.currentlabel.ref[:])

        # Resolve any outstanding references to this object
        if self.refs.has_key(label) and self.labels.has_key(label):
            for obj in self.refs[label]:
                for key, value in obj.idref.items():
                    if value.id != label:
                        continue
                    obj.idref[key] = self.labels[label]
            del self.refs[label]

    def ref(self, obj, name, label):
        """
        Set up a ref for resolution

        Required Arguments:
        obj -- object to put the referenced object onto
        name -- name of key in idref dictionary where object is stored
        label -- label to resolve

        See Also:
        self.label()

        """
        label = label.strip()
        if not label:
            return

        # Resolve ref if label already exists
        if self.labels.has_key(label):
            obj.idref[name] = self.labels[label]
            return 

        # If the label doesn't exist, store away the object for later
        if not self.refs.has_key(label):
            self.refs[label] = []
        self.refs[label].append(obj)

        # Make a fake node with the ID on it for now
        node = self['Macro']()
        node.id = label
        obj.idref[name] = node

    def __getitem__(self, key):
        """ 
        Look through the stack of macros and return the requested one 

        Required Arguments:
        key -- name of macro

        Returns: instance of requested macro

        """
        try: return self.top[key]
        except KeyError: pass

        # Didn't find it, so generate a new class
        if self.warnOnUnrecognized and not self.isMathMode:
            log.warning('unrecognized command/environment: %s', key)
        self[key] = newclass = new.classobj(str(key), (plasTeX.UnrecognizedMacro,), {})
        return newclass

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
                # If we hit a document element, make sure that we start
                # at the global context.
                if context.level == context.DOCUMENT_LEVEL:
                    while len(self.contexts) > 1:
                        self.contexts.pop()
            stacklog.debug('pushing %s onto %s', name, self.top)
            self.contexts.append(self.createContext(context))

        self.mapMethods()

    append = push

    def mapMethods(self):
        # Getter methods use the most local context
        self.top = top = self.contexts[-1]
        self.__getitem__ = top.__getitem__
        self.__contains__ = top.__contains__
        self.get = top.get
        self.keys = top.keys
        self.has_key = top.has_key
        self.categories = top.categories

        # Setter methods always use the global namespace
        self.update = top.update
        self.__setitem__ = self.contexts[0].__setitem__

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
#           if obj.categories is not None:
#               newcontext.categories = obj.categories

            newcontext.update(obj.locals())

        return newcontext

    def importMacros(self, context):
        """ 
        Import macros from given context into the global namespace

        Required Arguments:
        context -- dictionary of macros to import

        """
        for value in context.values():
            if ismacro(value):
                self[macroName(value)] = value
#           elif isinstance(value, Context):
#               self.importMacros(value)

    def pop(self, obj=None):
        """ 
        Remove a context from the stack 

        Keyword Arguments:
        index -- index of context item to remove

        Returns: ContextItem instance removed from stack

        """
#       print 'POP', type(obj).__name__, self.contexts[-1]
        if obj is None:
            # Pop until we hit a None in the context
            while len(self.contexts) > 1:
                if self.contexts[-1].obj is None:
                    self.contexts.pop()
                    break
                self.contexts.pop()
        else:
            while len(self.contexts) > 1:
                o = self.contexts[-1].obj
                # If None, keep going
                if o is None:
                    pass
                # Found context pushed by ourself
                elif o is obj:
                    self.contexts.pop()
                    break
                # Don't pop parent node
                elif o is obj.parentNode:
                    break
                # Found the \begin to our \end
                elif type(obj) == type(o) and obj.macroMode == obj.MODE_END:
                    self.contexts.pop()
                    break
                # Found the \foo to our \endfoo
                elif obj.nodeName == ('end%s' % o.nodeName):
                    self.contexts.pop()
                    break
                self.contexts.pop()

        self.mapMethods()

    def addGlobal(self, key, value):
        """ 
        Add a macro to the global context 

        Required Arguments:
        key -- name of macro to add
        value -- item to add to the global namespace.  If the item
            is a macro instance, it is simply added to the namespace.
            If it is a string, it is converted into a string Command
            instance before being added.

        """
        if isinstance(value, basestring):
            newvalue = plasTeX.Command()
            newvalue.unicode = value
            value = newvalue

        elif not ismacro(value):
            raise ValueError, \
                  '"%s" does not implement the macro interface' % key

        self.contexts[0][macroName(value)] = value

    __setitem__ = addGlobal

    def addLocal(self, key, value):
        """ 
        Add a macro to the local context 

        Required Arguments:
        key -- name of macro to add
        value -- item to add to the global namespace.  If the item
            is a macro instance, it is simply added to the namespace.
            If it is a string, it is converted into a string Command
            instance before being added.

        """
        if isinstance(value, basestring):
            newvalue = plasTeX.Command()
            newvalue.unicode = value
            value = newvalue

        elif not ismacro(value):
            raise ValueError, \
                  '"%s" does not implement the macro interface' % key

        self.contexts[-1][macroName(value)] = value

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

    def newcounter(self, name, resetby=None, initial=0, format=None):
        """ 
        Create a new counter 

        This method corresponds to LaTeX's \\newcounter command

        Required Arguments:
        name -- name of the counter.  The generate counter class will
            use this name.  Also, a new macro called 'the<name>' will
            also be generated for the counter format.

        Keyword Arguments:
        resetby -- the name of the counter that this counter is reset by
        initial -- initial value for the counter

        """
        name = str(name)
        # Counter already exists
        if self.counters.has_key(name):
            macrolog.debug('counter %s already defined', name)
            return
        self.counters[name] = plasTeX.Counter(self, name, resetby, initial)

        if format is None:
            format = '${%s}' % name
        newclass = new.classobj('the'+name, (plasTeX.TheCounter,), 
                               {'format': format})
        self.addGlobal('the'+name, newclass)

    def newwrite(self, name, file):
        """
        Create a new output file

        Required Arguments:
        name -- the key name for the file
        file -- the file name to open

        """
        self.writes[name] = open(file, 'w')

    def newcount(self, name, initial=0):
        """ 
        Create a new count (like \\newcount)

        Required Arguments:
        name -- name of count to create
      
        Keyword Arguments:
        initial -- value to initialize to

        """
        name = str(name)
        # Generate a new count class
        macrolog.debug('creating count %s', name)
        newclass = new.classobj(name, (plasTeX.CountCommand,), 
                               {'value': plasTeX.count(initial)})
        self.addGlobal(name, newclass)

    def newdimen(self, name, initial=0):
        """ 
        Create a new dimen (like \\newdimen)

        Required Arguments:
        name -- name of dimen to create
      
        Keyword Arguments:
        initial -- value to initialize to

        """
        name = str(name)
        # Generate a new dimen class
        macrolog.debug('creating dimen %s', name)
        newclass = new.classobj(name, (plasTeX.DimenCommand,), 
                                {'value': plasTeX.dimen(initial)})
        self.addGlobal(name, newclass)

    def newskip(self, name, initial=0):
        """ 
        Create a new glue (like \\newskip)

        Required Arguments:
        name -- name of glue to create
      
        Keyword Arguments:
        initial -- value to initialize to

        """
        name = str(name)
        # Generate a new glue class
        macrolog.debug('creating dimen %s', name)
        newclass = new.classobj(name, (plasTeX.GlueCommand,), 
                                {'value': plasTeX.glue(initial)})
        self.addGlobal(name, newclass)

    def newmuskip(self, name, initial=0):
        """ 
        Create a new muglue (like \\newmuskip)

        Required Arguments:
        name -- name of muglue to create
      
        Keyword Arguments:
        initial -- value to initialize to

        """
        name = str(name)
        # Generate a new muglue class
        macrolog.debug('creating muskip %s', name)
        newclass = new.classobj(name, (plasTeX.MuGlueCommand,), 
                                {'value': plasTeX.muglue(initial)})
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
        newclass = new.classobj(truename, (plasTeX.IfTrue,), {'ifclass':ifclass})
        self.addGlobal(truename, newclass)

        # Create \iffalse macro
        falsename = name[2:]+'false'
        newclass = new.classobj(falsename, (plasTeX.IfFalse,), {'ifclass':ifclass})
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
            if not issubclass(self[name], (plasTeX.NewCommand, 
                                           plasTeX.Definition)):
                if not issubclass(self[name], plasTeX.TheCounter):
                    return
            macrolog.debug('redefining command "%s"', name)

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
            if not issubclass(self[name], (plasTeX.NewCommand, 
                                           plasTeX.Definition)):
                return
            macrolog.debug('redefining environment "%s"', name)

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
            opt = [x for x in Tokenizer(opt, self)]

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
#       if self.has_key(name):
#           if not issubclass(self[name], (plasTeX.NewCommand, 
#                                          plasTeX.Definition)):
#               return
#           macrolog.debug('redefining definition "%s"', name)

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

    def chardef(self, name, num):
        """ 
        Create a \\chardef

        Required Arguments:
        name -- name of command to create
        num -- character number to use
      
        """
        name = str(name)
        # Generate a new chardef class
        macrolog.debug('creating chardef %s', name)
        newclass = new.classobj(name, (plasTeX.Command,), 
                                {'unicode':chr(num)})
        self.addGlobal(name, newclass)
