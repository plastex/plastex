#!/usr/bin/env python

__version__ = '9.3'

import string, re
from DOM import Element, Text, Node, DocumentFragment, Document
from Tokenizer import Token, BeginGroup, EndGroup, Other
from plasTeX import Logging, encoding

log = Logging.getLogger()
status = Logging.getLogger('status')
deflog = Logging.getLogger('parse.definitions')

#
# Utility functions
#

def idgen():
    """ Generate a unique ID """
    i = 1
    while 1:
        yield 'a%.10d' % i
        i += 1
idgen = idgen()

def subclasses(o):
    """ Return all subclasses of the given class """
    output = [o]
    for item in o.__subclasses__():
        output.extend(subclasses(item))
    return output

def sourceChildren(o, par=True): 
    """ Return the LaTeX source of the child nodes """
    if o.hasChildNodes():
        if par:
            return u''.join([x.source for x in o.childNodes])
        else:
            source = []
            for par in o.childNodes:
                source += [x.source for x in par]
            return u''.join(source)
    return u''

def sourceArguments(o): 
    """ Return the LaTeX source of the arguments """
    return o.argSource

def ismacro(o): 
    """ Is the given object a macro? """
    return hasattr(o, 'macroName')

def issection(o): 
    """ Is the given object a section? """
    return o.level >= Node.DOCUMENT_LEVEL and o.level < Node.ENDSECTIONS_LEVEL 

def macroName(o):
     """ Return the macro name of the given object """
     if o.macroName is None:
         if type(o) is type:
             return o.__name__
         return type(o).__name__
     return o.macroName


class Argument(object):
    """ 
    Macro argument

    Argument strings in macros are compiled into Arguments
    once.  Then the compiled arguments can be used to get the 
    arguments thereafter.

    """
    def __init__(self, name, index, options={}):
        self.name = name
        self.index = index
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
    @property
    def inline(self):
        """ 
        Create an inline style representation

        Returns:
        string containing inline CSS

        """
        if not self:
            return None      
        return u'; '.join([u'%s:%s' % (x[0],x[1]) for x in self.items()])


class Macro(Element):
    """
    Base class for all macros

    """
    MODE_NONE = 0
    MODE_BEGIN = 1
    MODE_END = 2

    macroName = None        # TeX macro name (instead of class name)
    macroMode = MODE_NONE   # begin, end, or none
    mathMode = None

    # Node variables
    level = Node.COMMAND_LEVEL
    nodeType = Node.ELEMENT_NODE
    nodeValue = None

    # Counter associated with this macro
    counter = None

    # Value to return when macro is referred to by \ref
    ref = None

    # Attributes that should be persisted between runs for nodes 
    # that can be referenced.  This allows for cross-document links.
    refAttributes = ['macroName','ref','title','captionName','id','url']

    # Source of the TeX macro arguments
    argSource = ''

    # LaTeX argument template
    args = ''

    # Force there to be at least on paragraph in the content
    forcePars = False

    def persist(self, attrs=None):
        """ 
        Store attributes needed for cross-document links 

        This method really needs to be called by the renderer because
        the rendered versions of the attributes are needed.  If nested
        classes could be pickeled, we could just pickle the attributes.

        Keyword Arguments:
        attrs -- dictionary to populate with values.  If set to None,
            a new dictionary should be created.

        Returns: dictionary containing attributes to be persisted

        """
        if attrs is None:
            attrs = {}
        for name in self.refAttributes:
            value = getattr(self, name, None)
            if value is None:
                continue
            if isinstance(value, Node):
                value = u'%s' % unicode(value)
            attrs[name] = value
        return attrs

    def restore(self, attrs):
        """ 
        Restore attributes needed for cross-document links 

        Required Attributes:
        attrs -- dictionary of attributes to be set on self

        """
        remap = {'url':'urloverride'}
        for key, value in attrs.items():
            setattr(self, remap.get(key, key), value)

    @property
    def config(self):
        """ Shortcut to the document config """
        return self.ownerDocument.config

    @property
    def idref(self):
        """ Storage area for idref argument types """
        if hasattr(self, '@idref'):
            return getattr(self, '@idref')
        d = {}
        setattr(self, '@idref', d)
        return d

    def captionName():
        """ Name associated with the counter """
        def fget(self):
            if hasattr(self, '@captionName'):
                return getattr(self, '@captionName')
            self.captionName = name = self.ownerDocument.createTextNode('')
            return name
        def fset(self, value):
            setattr(self, '@captionName', value)
        return locals()
    captionName = property(**captionName())

    def title():
        """ Retrieve title from variable or attributes dictionary """
        def fget(self):
            try:
                return getattr(self, '@title')
            except AttributeError:
                try:
                    return self.attributes['title']
                except KeyError:
                    pass
            raise AttributeError, 'could not find attribute "title"'
        def fset(self, value):
            setattr(self, '@title', value)
        return locals()
    title = property(**title())

    def fullTitle():
        """ Retrieve title including the section number """
        def fget(self):
            try:
                return getattr(self, '@fullTitle')
            except AttributeError:
                if self.ref is not None:
                    fullTitle = self.ownerDocument.createDocumentFragment()
                    fullTitle.extend([self.ref, ' ', self.title], setParent=False)
                else:
                    fullTitle = self.title
                setattr(self, '@fullTitle', fullTitle)
                return fullTitle
        def fset(self, value):
            setattr(self, '@fullTitle', value)
        return locals()
    fullTitle = property(**fullTitle())

    def tocEntry():
        """ Retrieve table of contents entry """
        def fget(self):
            try:
                return getattr(self, '@tocEntry')
            except AttributeError:
                try:
                    if self.attributes.has_key('toc'):
                        toc = self.attributes['toc']
                        if toc is None:
                            toc = self.title
                        setattr(self, '@tocEntry', toc)
                        return toc
                except (KeyError, AttributeError):
                    pass
            return self.title
        def fset(self, value):
            setattr(self, '@tocEntry', value)
        return locals()
    tocEntry = property(**tocEntry())

    def fullTocEntry():
        """ Retrieve title including the section number """
        def fget(self):
            try:
                try:
                    return getattr(self, '@fullTocEntry')
                except AttributeError:
                    if self.ref is not None:
                        fullTocEntry = self.ownerDocument.createDocumentFragment()
                        fullTocEntry.extend([self.ref, ' ', self.tocEntry], setParent=False)
                    else:
                        fullTocEntry = self.tocEntry
                    setattr(self, '@fullTocEntry', fullTocEntry)
                    return fullTocEntry
            except Exception, msg:
                return self.title
        def fset(self, value):
            setattr(self, '@fullTocEntry', value)
        return locals()
    fullTocEntry = property(**fullTocEntry())

    @property
    def style(self):
        """ CSS styles """
        try:
            return getattr(self, '@style')
        except AttributeError:
            style = CSSStyles()
            setattr(self, '@style', style)
        return style

    def digest(self, tokens):
        pass

    def locals(self):
        """ Retrieve all macros local to this namespace """
        tself = type(self)
        localsname = '@locals'
        # Check for cached versions first
        try:
            return vars(tself)[localsname]
        except KeyError:
            pass
        mro = list(tself.__mro__)
        mro.reverse()
        loc = {}
        for cls in mro:
            for value in vars(cls).values():
                if ismacro(value):
                    loc[macroName(value)] = value
        # Cache the locals in a unique name
        setattr(tself, localsname, loc)
        return loc

    def id():
        def fset(self, value):
            if value:
                setattr(self, '@id', value)
            else:
                delattr(self, '@id')
        def fget(self):
            id = getattr(self, '@id', None)
            if id is None: 
                for id in idgen:
                    setattr(self, '@hasgenid', True)
                    self.id = id
                    break
            return id
        return locals()
    id = property(**id())

    def expand(self, tex):
        """ Fully expand the macro """
        result = self.invoke(tex)
        if result is None:
            return self
        return tex.expandTokens(result)

    def invoke(self, tex):
        # Just pop the context if this is a \end token
        if self.macroMode == Macro.MODE_END:
            self.ownerDocument.context.pop(self)
            # If a unicode value is set, just return that
#           if self.unicode is not None:
#               return tex.textTokens(self.unicode)
            return

        # If this is a \begin token or the element needs to be
        # closed automatically (i.e. \section, \item, etc.), just 
        # push the new context and return the instance.
        elif self.macroMode == Macro.MODE_BEGIN:
            self.ownerDocument.context.push(self)
            self.parse(tex)
            # If a unicode value is set, just return that
#           if self.unicode is not None:
#               return tex.textTokens(self.unicode)
            self.setLinkType()
            return

        # Push, parse, and pop.  The command doesn't need to stay on
        # the context stack.  We push an empty context so that the
        # `self' token doesn't get put into the output stream twice
        # (once here and once with the pop).
        self.ownerDocument.context.push(self)
        self.parse(tex)
        self.ownerDocument.context.pop(self)

        # If a unicode value is set, just return that
#       if self.unicode is not None:
#           return tex.textTokens(self.unicode)

        self.setLinkType()

    def setLinkType(self, key=None):
        """ 
        Set up navigation links 

        Keyword Arguments:
        key -- the name or names of the navigation keys to set
            instead of using self.linkType

        """
        if key is None:
            key = self.linkType
        if key:
            userdata = self.ownerDocument.userdata
            if 'links' not in userdata:
                userdata['links'] = {}
            if isinstance(key, basestring):
                userdata['links'][key] = self
            else:
                for k in key:
                    userdata['links'][k] = self

    @property
    def tagName(self):
        t = type(self)
        if t.macroName is None:
            return t.__name__
        return t.macroName
    nodeName = tagName

    @property
    def source(self):
        name = self.nodeName

        # Automatically revert internal names like "active::~"
        escape = '\\'
        if '::' in name:
            name = name.split('::').pop()
            escape = ''

        # \begin environment
        # If self.childNodes is not empty, print out the entire environment
        if self.macroMode == Macro.MODE_BEGIN:
            argSource = sourceArguments(self)
            if not argSource: 
                argSource = ' '
            s = '%sbegin{%s}%s' % (escape, name, argSource)
            if self.hasChildNodes():
                s += '%s%send{%s}' % (sourceChildren(self), escape, name)
            return s

        # \end environment
        if self.macroMode == Macro.MODE_END:
            return '%send{%s}' % (escape, name)

        argSource = sourceArguments(self)
        if not argSource:
            argSource = ' '
        elif argSource[0] in encoding.stringletters():
            argSource = ' %s' % argSource
        s = '%s%s%s' % (escape, name, argSource)

        # If self.childNodes is not empty, print out the contents
        if self.attributes and self.attributes.has_key('self'):
            pass
        else:
            if self.hasChildNodes():
                s += sourceChildren(self)
        return s

    @property
    def childrenSource(self):
        return sourceChildren(self)

    def parse(self, tex): 
        """ 
        Parse the arguments defined in the `args` variable 

        Required Arguments:
        tex -- the TeX stream to parse from

        Returns:
        self.attributes

        """
        if self.macroMode == Macro.MODE_END:
            return

        self.preParse(tex)

        # args is empty, don't parse
        if not self.args:
            self.postParse(tex)
            return

        self.argSource = ''
        arg = None
        try:
            for arg in self.arguments:
                self.preArgument(arg, tex)
                output, source = tex.readArgumentAndSource(parentNode=self, 
                                                           name=arg.name, 
                                                           **arg.options)
                self.argSource += source
                self.attributes[arg.name] = output
                self.postArgument(arg, output, tex)
        except:
            raise
            log.error('Error while parsing argument "%s" of "%s"' % 
                       (arg.name, self.nodeName))

        self.postParse(tex)

        return self.attributes

    def preParse(self, tex):
        """
        Do operations that must be done immediately before parsing arguments

        Required Arguments:
        tex -- the TeX instance containing the current context

        """
        if not self.args:
            self.refstepcounter(tex)

    def preArgument(self, arg, tex):
        """ 
        Event called before parsing each argument

        Arguments:
        arg -- the Argument instance that holds all argument meta-data
            including the argument's name, source, and options.
        tex -- the TeX instance containing the current context 

        """
        # Check for a '*' type argument at the beginning of the
        # argument list.  If there is one, don't increment counters
        # or set labels.  This must be done immediately since
        # the following arguments may contain labels.
        if arg.index == 0 and arg.name != '*modifier*':
            self.refstepcounter(tex)

    def postArgument(self, arg, value, tex):
        """ 
        Event called after parsing each argument

        Arguments:
        arg -- the Argument instance that holds all argument meta-data
            including the argument's name, source, and options.
        tex -- the TeX instance containing the current context 

        """      
        # If there was a '*', unset the counter for this instance
        if arg.index == 0 and arg.name == '*modifier*':
            if value:
                self.counter = ''
            self.refstepcounter(tex)

    def stepcounter(self, tex):
        """
        Increment the counter for the object (if one exists)

        Required Arguments:
        tex -- the TeX instance containing the current context

        """
        if self.counter:
            try:
                self.ownerDocument.context.counters[self.counter].stepcounter()
            except KeyError:
                log.warning('Could not find counter "%s"', self.counter)
                self.ownerDocument.context.newcounter(self.counter,initial=1)

    def refstepcounter(self, tex):
        """
        Increment the counter for the object (if one exists)

        In addition to stepping the counter, the current object is 
        set as the currently labeled object.

        Required Arguments:
        tex -- the TeX instance containing the current context

        """
        if self.counter:
            self.ownerDocument.context.currentlabel = self
            self.stepcounter(tex)

    def postParse(self, tex):
        """
        Do operations that must be done immediately after parsing arguments

        Required Arguments:
        tex -- the TeX instance containing the current context

        """
        if self.counter:
            try: secnumdepth = self.config['document']['sec-num-depth']
            except: secnumdepth = 10
            if secnumdepth >= self.level or self.level > self.ENDSECTIONS_LEVEL:
                self.ref = self.ownerDocument.createElement('the'+self.counter).expand(tex)
                self.captionName = self.ownerDocument.createElement(self.counter+'name').expand(tex)

    @property
    def arguments(self):
        """ 
        Compile the argument string into function call arguments 

        Returns:
        arguments as compiled entities

        """
        tself = type(self)

        # Check for cached version first
        if vars(tself).has_key('@arguments'):
            return vars(tself)['@arguments']

        # If the argument string is empty, short circuit
        if not tself.args:
            setattr(tself, '@arguments', [])
            return getattr(tself, '@arguments')

        # Split the arguments into their primary components
        args = iter([x.strip() for x in 
                     re.split(r'(\w+(?::\w+(?:\(\S\))?(?::\w+)?)?|\W|\s+)', 
                              tself.args) if x is not None and x.strip()])

        groupings = {'[':'[]','(':'()','<':'<>','{':'{}'}

        macroargs = []
        argdict = {}
        index = 0
        for item in args:

            # Modifier argument
            if item in '*+-':
                if argdict:
                    raise ValueError, \
                        'Improperly placed "%s" in argument string "%s"' % \
                        (item, tself.args)
                argdict.clear()
                macroargs.append(Argument('*modifier*', index, {'spec':item}))
                index += 1

            # Optional equals
            elif item in '=':
                argdict.clear()
                macroargs.append(Argument('*equals*', index, {'spec':item}))
                index += 1

            # Beginning of group
            elif item in '[(<{':
                argdict.clear()
                argdict['spec'] = groupings[item]

            # End of group
            elif item in '])>}':
                pass

            # Argument name (and possibly type)
            elif item[0] in encoding.stringletters():
                parts = item.split(':')
                item = parts.pop(0)
                # Parse for types and subtypes
                if parts: 
                    # We already have a type, so check for subtypes
                    # for list items
                    if argdict.has_key('type'):
                        argdict['subtype'] = parts.pop(0)
                    else:
                        # Split type and possible delimiter
                        argdict['type'], argdict['delim'] = re.search(r'(\w+)(?:\((\W)\))?', parts.pop(0)).groups()
                        if parts:
                            argdict['subtype'] = parts.pop(0)
                # Arguments that are instance variables are always expanded
                if argdict.get('type') in ['cs','nox']:
                    argdict['expanded'] = False
                else:
                    argdict['expanded'] = True
                macroargs.append(Argument(item, index, argdict))
                index += 1
                argdict.clear()

            else:
                raise ValueError, 'Could not parse argument string "%s", reached unexpected "%s"' % (tself.args, item)

        # Cache the result
        setattr(tself, '@arguments', macroargs)

        return macroargs

    def digestUntil(self, tokens, endclass):
        """
        Absorb tokens until a token of the given class is given

        This method is useful for things like lists and tables 
        when one element is actually ended by the occurrence of 
        another (i.e. \\item ended by \\item, array cell ended by 
        array cell, array cell ended by array row, etc.).

        Required Arguments:
        tokens -- iterator of tokens in the stream
        endclass -- class reference or tuple of class references
            that, when a token of that type is reached, stops
            the digestion process

        Returns:
        None -- if the context ended without reaching a token of
            the requested type
        token -- the token of the requested type if it was found

        """
        for tok in tokens:
            if tok.nodeType == Node.ELEMENT_NODE:
                if isinstance(tok, endclass):
                    tokens.push(tok)
                    return tok
                tok.parentNode = self
                tok.digest(tokens)
            # Stay within our context
            if tok.contextDepth < self.contextDepth:
                tokens.push(tok)
                break
            self.appendChild(tok)

    @property
    def currentSection(self):
        """
        Return the section that this node belongs to

        This property will contain the parent section if the current
        node is a section node.

        """
        node = self.parentNode
        while node is not None:
            if node.level < Node.ENDSECTIONS_LEVEL:
                return node
            node = node.parentNode
        return
        
    def paragraphs(self, force=True):
        """
        Group content into paragraphs

        This algorithm is based on TeX's paragraph grouping algorithm.
        This has the downside that it isn't the same paragraph algorithm
        as HTML which doesn't allow block-level elements (e.g. table,
        ol, ul, etc.) inside paragraphs.  This will result in invalid
        HTML, but it isn't likely to be noticed in a browser.

        Keyword Arguments:
        force -- force all content to be grouped into paragraphs even
            if there are no paragraps already present

        """
        parname = None
        for item in self:
            if item.level == Node.PAR_LEVEL:
                parname = item.nodeName
                break

        # No paragraphs, and we aren't forcing paragraphs...
        if parname is None and not force:
            self.normalize(self.ownerDocument.charsubs)
            return

        if parname is None:
            parname = 'par'

        # Group content into paragraphs
        par = self.ownerDocument.createElement(parname)
        par.parentNode = self
        newnodes = [par]
        while self:
            item = self.pop(0)
            if item.level == Node.PAR_LEVEL:
                newnodes.append(item)
                continue
            if item.level < Node.PAR_LEVEL:
                newnodes.append(item)
                break
            # Block level elements get their own paragraph
            if item.blockType:
                par = self.ownerDocument.createElement(parname)
                par.appendChild(item)
                par.blockType = True
                newnodes.append(par)
                par = self.ownerDocument.createElement(parname)
                newnodes.append(par)
                continue
            newnodes[-1].append(item)

        # Insert nodes into self
        for i, item in enumerate(newnodes):
            if item.level == Node.PAR_LEVEL:
                item.normalize(self.ownerDocument.charsubs)
            self.insert(i, item)

        # Filter out any empty paragraphs
        for i in range(len(self)-1, -1, -1):
            item = self[i]
            if item.level == Node.PAR_LEVEL:
                if len(item) == 0:
                    self.pop(i)
                elif len(item) == 1 and item[0].isElementContentWhitespace:
                    self.pop(i)

class TeXFragment(DocumentFragment):
    """ Document fragment node """
    @property
    def source(self):
        return sourceChildren(self)

class TeXDocument(Document):
    """ TeX Document node """
    documentFragmentClass = TeXFragment

    # Character sequences that should be replaced by unicode
    charsubs = [
        ('``', unichr(8220)),
        ("''", unichr(8221)),
        ('"`', unichr(8222)),
        ('"\'', unichr(8220)),
        ('`',  unichr(8216)),
        ("'",  unichr(8217)),
        ('---',unichr(8212)),
        ('--', unichr(8211)),
#       ('fj', unichr(58290)),
#       ('ff', unichr(64256)),
#       ('fi', unichr(64257)),
#       ('fl', unichr(64258)),
#       ('ffi',unichr(64259)),
#       ('ffl',unichr(64260)),
#       ('ij', unichr(307)),
#       ('IJ', unichr(308)),
    ]

    def __init__(self, *args, **kwargs):
        #super(TeXDocument, self).__init__(*args, **kwargs)

        if 'context' not in kwargs:
            import Context
            self.context = Context.Context(load=True)
        else:
            self.context = kwargs['context']

        if 'config' not in kwargs:
            import Config
            self.config = Config.config
        else:
            self.config = kwargs['config']

        # post parsing callbacks list
        self.post_parse_cb = []

    def createElement(self, name):
        elem = self.context[name]()
        elem.parentNode = None
        elem.ownerDocument = self
        elem.contextDepth = 1000
        return elem

    @property
    def preamble(self):
        """
        Return the nodes in the document that correspond to the preamble

        """
        output = self.createDocumentFragment()
        for item in self:
            if item.level == Macro.DOCUMENT_LEVEL:
                break
            output.append(item)
        return output

    @property
    def source(self):
        """ Return the LaTeX source of the document """
        return sourceChildren(self)

class Command(Macro): 
    """ Base class for all Python-based LaTeX commands """

class Environment(Macro): 
    """ Base class for all Python-based LaTeX environments """
    level = Node.ENVIRONMENT_LEVEL

    def invoke(self, tex):
        if self.macroMode == Macro.MODE_END:
            self.ownerDocument.context.pop(self)
            # If a unicode value is set, just return that
            if self.unicode is not None:
                return tex.textTokens(self.unicode)
            return

        self.ownerDocument.context.push(self)
        self.parse(tex)

        # If a unicode value is set, just return that
        if self.unicode is not None:
            return tex.textTokens(self.unicode)

        self.setLinkType()

    def digest(self, tokens):
        """ Absorb all of the tokens that belong to the environment """
        if self.macroMode == Macro.MODE_END:
            return
        # Absorb the tokens that belong to us
        dopars = self.forcePars
#       print 'DIGEST', type(self), self.contextDepth
        for item in tokens:
#           print type(item), (item.level, self.level), (item.contextDepth, self.contextDepth)
            # Make sure that we know to group paragraphs if one is found
            if item.level == Node.PAR_LEVEL:
                self.appendChild(item)
                dopars = True
                continue
            # Don't absorb objects with a higher precedence
            if item.level < self.level:
                tokens.push(item)
                break
            # Absorb macros until the end of this environment is found
            if item.nodeType == Node.ELEMENT_NODE:
                if item.macroMode == Macro.MODE_END and type(item) is type(self):
                    break
                item.parentNode = self
                item.digest(tokens)
            # Stay within our context depth
            if self.level > Node.DOCUMENT_LEVEL and \
               item.contextDepth < self.contextDepth:
                tokens.push(item)
                break
#           print 'APPEND', type(item)
            self.appendChild(item)
#       print 'DONE', type(self)
        if dopars:
            self.paragraphs()


class NoCharSubEnvironment(Environment):
    """
    A subclass of Environment which prevents character substitution inside
    itself.
    """
    def __init__(self, *args, **kwargs):
        # Will hold the owner document charsubs to restore it at the end
        self.charsubs = []
        super(NoCharSubEnvironment, self).__init__(*args, **kwargs)

    def invoke(self, tex):
        # The goal is to prevent any character substitution while handling a
        # this environment.
        doc = self.ownerDocument
        if self.macroMode == Macro.MODE_BEGIN:
            self.charsubs = doc.charsubs
            doc.charsubs = []
        elif self.macroMode == Macro.MODE_END:
            doc.charsubs = self.charsubs
        super(NoCharSubEnvironment, self).invoke(tex)

class IgnoreCommand(Command):
    """
    This command will be parsed, but will not go to the output stream

    This should be used sparingly because it also means that if you
    try to access the source of a node in a document, this will also
    be missing from that.

    """
    def invoke(self, tex):
        Command.invoke(self, tex)
        return []

class UnrecognizedMacro(Macro):
    """
    Base class for unrecognized macros

    When an unrecognized macro is requested, an instance of this 
    class is generated as a placeholder for the missing macro.

    """
    def __cmp__(self, other):
        if not hasattr(other, 'nodeName'):
            return 0
        if other.nodeName in ['undefined','@undefined']:
            return 0
        if isinstance(other, UnrecognizedMacro):
            return 0
        return super(UnrecognizedMacro, self).__cmp__(other)

class NewIf(Macro):
    """ Base class for all generated \\newifs """

    state = False

    def invoke(self, tex):
        tex.processIfContent(type(self).state)
        return []

    @classmethod
    def setState(cls, state):
        cls.state = state

    @classmethod
    def setTrue(cls):
        cls.state = True

    @classmethod
    def setFalse(cls):
        cls.state = False

class IfTrue(Macro):
    """ Base class for all generated \\iftrues """
    def invoke(self, tex):
        type(self).ifclass.setTrue()
        return []

class IfFalse(Macro):
    """ Base class for all generated \\iffalses """
    def invoke(self, tex):
        type(self).ifclass.setFalse()
        return []

def expandDef(definition, params):
    # Walk through the definition and expand parameters
    if not definition:
        return []
    output = []
    definition = iter(definition)
    previous = ''
    for t in definition:
        # Expand parameters
        if t.catcode == Token.CC_PARAMETER:
            for t in definition:
                # Double '#'
                if t.catcode == Token.CC_PARAMETER:
                    output.append(t)
                else:
                    if params[int(t)] is not None:
                        # This is a pretty bad hack, but `ifx' commands
                        # need an argument to also be a token.  So we
                        # wrap them in a group here and let the 
                        # TeX parser convert the group to a token. 
                        if previous == 'ifx':
                            output.append(BeginGroup(' '))
                            output.extend(params[int(t)])
                            output.append(EndGroup(' '))
                        else:
                            output.extend(params[int(t)])
                break
        # Just append other tokens to the output
        else:
            output.append(t)
        previous = t
    return output

class NewCommand(Macro):
    """ Superclass for all \newcommand/\newenvironment type commands """
    nargs = 0
    opt = None
    definition = None

    def invoke(self, tex):
        if self.macroMode == Macro.MODE_END:
            res = self.ownerDocument.createElement('end'+self.tagName).invoke(tex)
            if res is None:
                return [res, EndGroup(' ')]
            return res + [EndGroup(' ')]

        params = [None]

        # Get optional argument, if needed
        nargs = self.nargs
        if self.opt is not None:
            nargs -= 1
            params.append(tex.readArgument('[]', default=self.opt, 
                                           parentNode=self, 
                                           name='#%s' % len(params)))

        # Get mandatory arguments
        for i in range(nargs):
            params.append(tex.readArgument(parentNode=self, 
                                           name='#%s' % len(params)))

        deflog.debug2('expanding %s %s', self.definition, params)

        output = []
        if self.macroMode == Macro.MODE_BEGIN:
            output.append(BeginGroup(' '))
            
        return output + expandDef(self.definition, params)

class Definition(Macro):
    """ Superclass for all \\def-type commands """
    args = None
    definition = None

    def invoke(self, tex):
        if not self.args: return self.definition

        name = macroName(self)
        argIter = iter(self.args)
        inparam = False
        params = [None]
        for a in argIter:

            # Beginning a new parameter
            if a.catcode == Token.CC_PARAMETER:
                
                # Adjacent parameters, just get the next token
                if inparam:
                    params.append(tex.readArgument(parentNode=self,
                                                   name='#%s' % len(params)))

                # Get the parameter number
                for a in argIter:
                    # Numbered parameter
                    if a in string.digits:
                        inparam = True

                    elif a.catcode == Token.CC_PARAMETER:
                        continue
                    
                    # Handle #{ case here
                    elif a.catcode == Token.CC_BGROUP:
                        param = []
                        for t in tex.itertokens():
                            if t.catcode == Token.CC_BGROUP:
                                tex.pushToken(t)
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
                        log.info('Arguments of "%s" don\'t match definition. Got "%s" but was expecting "%s" (%s).' % (name, t, a, ''.join(self.args)))
                        break

        if inparam:
            params.append(tex.readArgument(parentNode=self, 
                                           name='#%s' % len(params)))

        deflog.debug2('expanding %s %s', self.definition, params)

        return expandDef(self.definition, params)


class number(int):
    """ Class used for parameter and count values """
    def __new__(cls, v):
        if isinstance(v, Macro):
            return v.__count__()
        return int.__new__(cls, v)

    @property
    def source(self):
        return unicode(self)

class count(number): pass

class dimen(float):
    """ Class used for dimen values """

    units = ['pt','pc','in','bp','cm','mm','dd','cc','sp','ex','em']

    def __new__(cls, v):
        if isinstance(v, Macro):
            return v.__dimen__()
        elif isinstance(v, basestring) and v[-1] in encoding.stringletters():
            # Get rid of glue components
            v = list(v.split('plus').pop(0).split('minus').pop(0).strip())
            units = []
            while v and v[-1] in encoding.stringletters():
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

    @property
    def source(self):
        sign = 1
        if self < 0:
            sign = -1
        if abs(self) >= 6e9:
            return unicode(sign * (abs(self)-6e9)) + 'filll'
        if abs(self) >= 4e9:
            return unicode(sign * (abs(self)-4e9)) + 'fill'
        if abs(self) >= 2e9:
            return unicode(sign * (abs(self)-2e9)) + 'fil'
        return '%spt' % self.pt

    @property
    def pt(self): 
        return self / 65536
    point = pt

    @property
    def pc(self): 
        return self / (12 * 65536)
    pica = pc

    @property
    def _in(self): 
        return self / (72.27 * 65536)
    inch = _in

    @property
    def bp(self): 
        return self / ((72.27 * 65536) / 72)
    bigpoint = bp

    @property
    def cm(self): 
        return self / ((72.27 * 65536) / 2.54)
    centimeter = cm

    @property
    def mm(self): 
        return self / ((72.27 * 65536) / 25.4)
    millimeter = mm

    @property
    def dd(self): 
        return self / ((1238 * 65536) / 1157)
    didotpoint = dd

    @property
    def cc(self): 
        return self / ((1238 * 12 * 65536) / 1157)
    cicero = cc

    @property
    def sp(self): 
        return self
    scaledpoint = sp

    @property
    def ex(self): 
        return self / (5 * 65536)
    xheight = ex

    @property
    def em(self): 
        return self / (11 * 65536)
    mwidth = em

    @property
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
    fil = filll = fill

    def __repr__(self):
        return self.source

    def __str__(self):
        return self.source

class mudimen(dimen):
    """ Class used for mudimen values """
    units = ['mu']

class glue(dimen):
    """ Class used for glue values """
    def __new__(cls, g, plus=None, minus=None):
        return dimen.__new__(cls, g)
        
    def __init__(self, g, plus=None, minus=None):
        #super(glue, self).__init__(g)
        self.stretch = self.shrink = None
        if plus is not None:
            self.stretch = dimen(plus)
        if minus is not None:
            self.shrink = dimen(minus)

    @property
    def source(self):
        s = [dimen(self).source]
        if self.stretch is not None:
            s.append('plus')
            s.append(self.stretch.source)
        if self.shrink is not None:
            s.append('minus')
            s.append(self.shrink.source)
        return ' '.join(s)

class muglue(glue): 
    """ Class used for muglue values """
    units = ['mu']


class ParameterCommand(Command):
    args = '= value:Number'
    value = count(0)

    enabled = True
    _enablelevel = 0
    
    def invoke(self, tex):
        if ParameterCommand.enabled:
            # Disable invoke() in parameters nested in our arguments.
            # We don't want them to invoke, we want them to set our value.
            ParameterCommand.enabled = False
            type(self).value = self.parse(tex)['value']
            ParameterCommand.enabled = True

    @classmethod
    def enable(cls):
        ParameterCommand._enablelevel += 1
        ParameterCommand.enabled = ParameterCommand._enablelevel >= 0 

    @classmethod
    def disable(cls):
        ParameterCommand._enablelevel -= 1
        ParameterCommand.enabled = ParameterCommand._enablelevel >= 0 

    def __dimen__(self):
        return dimen(type(self).value)

    def __mudimen__(self):
        return mudimen(type(self).value)

    def __count__(self):
        return count(type(self).value)

    def __glue__(self):
        return glue(type(self).value)
    
    def __muglue__(self):
        return muglue(type(self).value)

    def the(self):
        return type(self).value.source

    @classmethod
    def new(cls, *args, **kwargs):
        return count(*args, **kwargs)

class RegisterCommand(ParameterCommand): pass

class CountCommand(RegisterCommand): pass

class DimenCommand(RegisterCommand):
    args = '= value:Dimen'
    value = dimen(0)

    def setlength(self, len):
        type(self).value = dimen(len)

    def addtolength(self, len):
        type(self).value = dimen(type(self).value + len)

    @classmethod
    def new(cls, *args, **kwargs):
        return dimen(*args, **kwargs)

class MuDimenCommand(RegisterCommand):
    args = '= value:MuDimen'
    value = mudimen(0)

    def setlength(self, len):
        type(self).value = mudimen(len)

    def addtolength(self, len):
        type(self).value = mudimen(type(self).value + len)

    @classmethod
    def new(cls, *args, **kwargs):
        return mudimen(*args, **kwargs)

class GlueCommand(RegisterCommand):
    args = '= value:Glue'
    value = glue(0)

    def setlength(self, len):
        type(self).value = glue(len)

    def addtolength(self, len):
        type(self).value = glue(type(self).value + len)

    @classmethod
    def new(cls, *args, **kwargs):
        return glue(*args, **kwargs)

class MuGlueCommand(RegisterCommand):
    args = '= value:MuGlue'
    value = muglue(0)

    def setlength(self, len):
        type(self).value = muglue(len)

    def addtolength(self, len):
        type(self).value = muglue(type(self).value + len)

    @classmethod
    def new(cls, *args, **kwargs):
        return muglue(*args, **kwargs)


class Counter(object):
    """
    LaTeX counter class

    """
    def __init__(self, context, name, resetby=None, value=0):
        self.name = name
        self.resetby = resetby
        self.value = value
        self.counters = context.counters

    def addtocounter(self, other):
        self.value += int(other)
        self.resetcounters()

    def setcounter(self, other):
        self.value = int(other)
        self.resetcounters()

    def stepcounter(self):
        self.value += 1
        self.resetcounters()

    def resetcounters(self):
        for counter in self.counters.values():
            if counter.resetby and self.name and counter.resetby == self.name: 
                counter.value = 0
                counter.resetcounters()

    def __int__(self):
        return self.value

    def __float__(self):
        return self.value

    @property
    def arabic(self):
        return unicode(self.value)

    @property
    def Roman(self):
        roman = ""
        n, number = divmod(self.value, 1000)
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

    @property
    def roman(self):
        return self.Roman.lower()

    @property
    def Alph(self):
        return encoding.stringletters()[self.value-1].upper()

    @property
    def alph(self):
        return self.Alph.lower()

    @property
    def fnsymbol(self):
        return '*' * self.value


class TheCounter(Command):
    """ Base class for \\thecounter commands """
    format = None

    def invoke(self, tex):

        def counterValue(m):
            """ Replace the counter values """
            name = m.group(1)

            # If there is a reference to another \\thecounter, invoke it
            if name.startswith('the') and name != re.sub(r'^the', '', self.__class__.__name__):
                return u''.join(tex.expandTokens(self.ownerDocument.createElement(name).invoke(tex)))

            # Get formatted value of the requested counter
            format = m.group(2)
            if not format:
                format = 'arabic'

            return getattr(self.ownerDocument.context.counters[name], format)

        format = re.sub(r'\$(\w+)', r'${\1}', self.format)
        if self.format is None:
            format = '${%s.arabic}' % self.nodeName[3:]

        t = re.sub(r'\$\{\s*(\w+)(?:\.(\w+))?\s*\}', counterValue, format)

        # This is kind of a hack.  Since number formats aren't quite as 
        # flexible as in LaTeX, we have to do somethings heuristically.
        # In this case, whenever a counter value comes out as a zero,
        # just hank it out.  This is especially useful in document classes
        # such as book and report which do this in the \thefigure format macro.
        t = re.sub(r'\b0[^\dA-Za-z]+', r'', t)

        return tex.textTokens(t)
