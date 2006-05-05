#!/usr/bin/env python

import codecs, os
from plasTeX.DOM import Node
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')

__all__ = ['Renderer','Renderable']

def mixin(base, mix, overwrite=False):
    """
    Mix the methods and members of class `mix` into `base`

    Required Arguments:
    base -- the base class to add mixin to
    mix -- the mixin class

    """
    if not vars(base).has_key('_mixed_'):
        base._mixed_ = {}
    mixed = base._mixed_
    for item, value in vars(mix).items():
        if overwrite or not vars(base).has_key(item):
            old = vars(base).get(item, None)
            setattr(base, item, value)
            mixed[item] = (mix, old)

def unmix(base, mix=None):
    """
    Remove mixed in methods and members 

    Required Arguments:
    base -- the base class to remove mixins from

    Keyword Arguments:
    mix -- the mixin class to remove from `base`

    """
    if mix is None:
        for key, value in base._mixed_.items():
            if value[1] is not None:
                setattr(base, key, value[1])
            else:
                delattr(base, key)
        del base._mixed_
    else:
        for key, value in base._mixed_.items():
            if value[0] is mix:
                if value[1] is not None:
                    setattr(base, key, value[1])
                else:
                    delattr(base, key)
        if not base._mixed_:
            del base._mixed_


class Renderer(dict):
    """
    Base class for all renderers

    All renderers must act like a dictionary.  Each macro that is encountered
    in a document must have a corresponding key in the renderer.  This 
    key points to a callable object which is called with the object to
    be rendered.

    In addition to callable renderers, the renderer also handles image 
    generation.  Images are generated when the output document type can 
    not support the rendering of a macro.  One example of this is equations
    in HTML.

    """

    textdefault = unicode
    default = unicode
    outputtype = unicode

    def __init__(self, data={}):
        dict.__init__(self, data)

        # Names of generated files
        self.files = []

        # Instantiated at render time
        self.imager = None

        # Filename generator
        self.newfilename = None

        self.previous = None

        # Call the initialization hook
        self.initialize()

    def initialize(self):
        """ Invoke any setup that needs to be done before rendering """
        pass

    def loadImager(self, document):
        """ Load the class responsible for generating images """
        if not document.userdata['config']['images']['enabled']:
            from plasTeX.Imagers import Imager
            self.imager = Imager(document)
            return

        name = document.userdata['config']['images']['program']

        try: 
            exec('from plasTeX.Imagers.%s import Imager' % name)
        except ImportError, msg:
            log.warning("Could not load imager '%s' because '%s'" % (name, msg))
            from plasTeX.Imagers import Imager
        
        self.imager = Imager(document)

    def unloadImager(self):
        if self.imager is not None:
            self.imager.close()

    def render(self, document):
        """
        Invoke the rendering process

        This method invokes the rendering process as well as handling
        the setup and shutdown of image processing.

        Required Arguments:
        document -- the document object to render

        """
        config = document.userdata['config']

        # If there are no keys, print a warning.  
        # This is most likely a problem.
        if not self.keys():
            log.warning('There are no keys in the renderer.  ' +
                        'All objects will use the default rendering method.')

        # Mix in required methods and members
        mixin(Node, Renderable)
        Node.renderer = self

        # Create a filename generator
        ns = {'jobname':document.userdata['jobname']}
        self.newfilename = GeneratorProxy(
                         filenames(config['files'].get('filename', raw=True), 
                         charsub=(config['files']['bad-chars'],
                                  config['files']['bad-chars-sub']), 
                         namespace=ns), namespace=ns)

        # Instantiate appropriate imager
        self.loadImager(document)

        # Add document preamble to image document
        self.imager.addtopreamble(document.preamble.source)

        # Invoke the rendering process
        result = unicode(document)

        # Close imager so it can finish processing
        self.unloadImager()

        # Run any cleanup activities
        self.cleanup(document, self.files)

        # Must wait until after cleanup to delete the imager
        self.imager = None

        # Remove mixins
        del Node.renderer
        unmix(Node, Renderable)

        #return result

    def cleanup(self, doc, files):
        """ Do any post-rending cleanup """
        pass

    def find(self, keys, default=None):
        """
        Locate a renderer given a list of possibilities
  
        Required Arguments:
        keys -- a list of strings containing the requested name of 
            a renderer.  This list is traversed in order.  The first 
            renderer that is found is returned.

        Keyword Arguments:
        default -- the renderer to return if none of the keys exists

        Returns:
        the requested renderer

        """
        for key in keys:
            if self.has_key(key):
                return self[key]

        # Text nodes get the textdefault
        if ''.join(keys) == '#text':
            if self.textdefault:
                return self.textdefault
            return default

        # Other nodes supplied default
        else:
            log.warning('Using default renderer for %s' % ', '.join(keys))
            for key in keys:
                self[key] = default
            return default


class Renderable(object):
    """
    Base class for all renderable nodes

    This class is mixed into nodes of the document object prior to 
    rendering.  The actual rendering method is __unicode__.

    """

    def __unicode__(self):
        """
        Invoke the rendering process on all of the child nodes.

        """
        # If we don't have childNodes, then we're done
        if not self.hasChildNodes():
            return u''

        # Store these away for efficiency
        r = Node.renderer
        filename = self.filename

        if filename:
            status.info(' [ %s ', filename)

        # Render all child nodes
        s = []
        for child in self.childNodes:
            names = []
            nodeName = child.nodeName

            # If the child is going to generate a new file, we should 
            # check for a template that has file wrapper content first.
            if self.nodeType == Node.ELEMENT_NODE:
                modifier = None

                # Does the macro have a modifier (i.e. '*')
                if child.attributes:
                    modifier = child.attributes.get('*modifier*')

                if child.filename:
                    # Filename and modifier
                    if modifier:
                        names.append('%s-file%s' % (nodeName, modifier))
                    # Filename only
                    names.append('%s-file' % nodeName)

                # Modifier only
                elif modifier:
                    names.append('%s%s' % (nodeName, modifier))

            names.append(nodeName)

            # Locate the rendering callable, and call it with the 
            # current object (i.e. `child`) as its argument.
            val = r.find(names, r.default)(child)

            if type(val) is not unicode:
                log.warning('The renderer for %s returned a non-unicode string.  Using the default input encoding.' % type(child).__name__)
                val = unicode(val, child.config['files']['input-encoding'])

            # If the content should go to a file, write it and go
            # to the next child.
            if child.filename:
                filename = child.filename
                directory = os.path.dirname(filename)
                if directory and not os.path.isdir(directory):
                    os.makedirs(directory)
                r.files.append(filename)
                codecs.open(filename, 'w', child.config['files']['output-encoding']).write(val)
                continue

            # Append the resultant unicode object to the output
            s.append(val)

        if filename:
            status.info(' ] ')

        return r.outputtype(u''.join(s))

    def __str__(self):
        return unicode(self)

    @property
    def image(self):
        """ Generate an image and return the image filename """
        return Node.renderer.imager.newimage(self.source)

    @property
    def url(self):
        """
        Return the relative URL of the object

        If the object actually creates a file, just the filename will
        be returned (e.g. foo.html).  If the object is within a file, 
        both the filename and the anchor will be returned 
        (e.g. foo.html#bar).

        """
        # If this generates a file, return that filename
        if self.filename:
            return URL(self.filename)

        # If this is a location within a file, return that location
        node = self.parentNode
        while node is not None and node.filename is None:
            node = node.parentNode
        filename = ''
        if node is not None:
            filename = node.filename
        return URL('%s#%s' % (filename, self.id))

    @property
    def filename(self):
        """
        The filename that this object should create

        Objects that don't create new files should simply return `None`.

        """
        try:
            return self.filenameoverride

        except AttributeError:
            if not hasattr(self, 'config'):
                self.filenameoverride = None
                return

            # If our level doesn't invoke a split, don't return a filename
            if self.level > self.config['files']['split-level']:
                self.filenameoverride = None
                return

            # Populate namespace of filename generator
            # and call the generator to get the filename.
            ns = Node.renderer.newfilename.namespace
            if hasattr(self, 'id') and self.id != ('a%s' % id(self)):
                ns['id'] = self.id
            if hasattr(self, 'title'):
                if hasattr(self.title, 'textContent'):
                    ns['title'] = self.title.textContent
                elif isinstance(self.title, basestring):
                    ns['title'] = self.title
            filename = Node.renderer.newfilename()

            # Store the name if this method is called again
            self.filenameoverride = filename

        return filename


def parsefilenames(spec):
    """ Parse and expand the filename string """
    import re

    # Normalize string before parsing
    spec = re.sub(r'\$(\w+)', r'${\1}', spec)
    spec = re.sub(r'\${\s*(\w+)\s*}', r'${\1}', spec)
    spec = re.sub(r'\}\(\s*(\d+)\s*\)', r'.\1}', spec)
    spec = re.sub(r'\[\s*', r'[', spec)
    spec = re.sub(r'\s*\]', r']', spec)
    spec = re.sub(r'\s*,\s*', r',', spec)

    files = ['']
    spec = iter(spec)
    for char in spec:

        # Spaces mark a division between names
        if not char.strip():
             files.append('')
             continue

        # Check for alternatives
        elif char == '[':
            options = [files[-1]]
            for char in spec:
                if char == ',':
                    options.append(files[-1])
                    continue
                elif char == ']':
                    break
                options[-1] += char
            files[-1] = [x for x in options if x]
            continue
        
        # Append the character to the current filename
        if isinstance(files[-1], list):
            for i, item in enumerate(files[-1]):
                files[-1][i] += char
        else:
            files[-1] += char

    files = [x for x in files if x]

    return files


def filenames(spec, charsub=[], namespace={}):
    """
    Generate filenames based on the `spec' and using the given namespace

    Arguments:
    spec -- string containing filename specifier.  The filename specifier
        is a list of space separated names.  Each name in the list is 
        returned once.  An example is shown below::

            index.html toc.html file1.html file2.html

        These filenames can also contain variables as described in 
        Python's string Templates (e.g. $title, ${id}).  These variables
        come from the `namespace' variable.  One special variable is
        $num.  This value in generated dynamically whenever a filename
        with $num is requested.  Each time a filename with $num is 
        successfully generated, the value of $num is incremented.

        The values of variables can also be modified by a format specified
        in parentheses after the variable.  The format is simply an integer
        that specifies how wide of a field to create for integers 
        (zero-padded), or, for strings, how many space separated words
        to limit the name to.  The example below shows $num being padded
        to four places and $title being limited to five words::

            sect$num(4).html $title(5).html

        The list can also contain a wildcard filename (which should be 
        specified last).  Once a wildcard name is reached, it is 
        used from that point on to generate the remaining filenames.  
        The wildcard filename contains a list of alternatives to use as
        part of the filename indicated by a comma separated list of 
        alternatives surrounded by a set of square brackets ([ ]).
        Each of the alternatives specified is tried until a filename is
        successfully created (i.e. all variables resolve).  For example,
        the specification below creates three alternatives::
 
            $jobname_[$id, $title, sect$num(4)].html

        The code above is expanded to the following possibilities::

            $jobname_$id.html
            $jobname_$title.html
            $jobname_sect$num(4).html

        Each of the alternatives is attempted until one of them succeeds.
        Generally, the last one should contain no variables except for
        $num as a fail-safe alternative.

    Keyword Arguments:
    charsub -- two-element list that contains character substitutions.
        The first element is a string containing all of the characters
        that are illegal in a filename.  The second string is a string
        that will be used in place of each of the "bad" characters in 
        resulting filename.
    namespace -- the namespace of variables to use when expanding the
        filenames.  New variables can be added to this namespace between
        each iteration.  The namespace is reset to the value sent in
        the initial generator call after each iteration.

    Returns:
    generator that creates filenames

    """
    import re
    from string import Template

    files = parsefilenames(spec)

    globals = namespace.copy()

    # Split filenames into static and wildcard groups
    static = []
    wildcard = []
    while files:
        if isinstance(files[0], list):
            break
        static.append(files.pop(0))
    if files:
        wildcard = files.pop(0)

    # Initialize file number counter
    num = 1

    # Locate all key names and formats in the string
    keysre = re.compile(r'\$\{(\w+)(?:\.(\d+))?}')

    # Return static filenames
    for item in static:
        currentns = namespace.copy()
        for key, value in currentns.items():
            for char in charsub[0]:
                currentns[key] = value.replace(char, charsub[1])
        for key, format in keysre.findall(item):
            # Supply a file number as needed
            if key == 'num':
                currentns['num'] = ('%%.%sd' % format) % num
            # Limit other variables to specified number of words
            elif format and key in currentns:
                value = currentns[key].split()
                newvalue = []
                for i in range(int(format)):
                    newvalue.append(value.pop(0))
                    if not value:
                        break
                currentns[key] = ' '.join(newvalue)
        try:
            # Strip formats
            item = re.sub(r'(\$\{\w+)\.\d+(\})', r'\1\2', item)
            # Do variable substitution
            result = Template(item).substitute(currentns)
            if 'num' in currentns:
                num += 1
            namespace.clear()
            namespace.update(globals)
            yield result
        except KeyError, key:
            continue
            
    # We've reached the wildcard stage.  The wildcard gives us
    # multiple alternatives of filenames to choose from.  Keep trying
    # each one with the current namespace until one works.
    while 1:
        for item in wildcard:
            currentns = namespace.copy()
            for key, value in currentns.items():
                for char in charsub[0]:
                    currentns[key] = value.replace(char, charsub[1])
            for key, format in keysre.findall(item):
                # Supply a file number as needed
                if key == 'num':
                    currentns['num'] = ('%%.%sd' % format) % num
                # Limit other variables to specified number of words
                elif format and key in currentns:
                    value = currentns[key].split()
                    newvalue = []
                    for i in range(int(format)):
                        newvalue.append(value.pop(0))
                        if not value:
                            break
                    currentns[key] = ' '.join(newvalue)
            try:
                # Strip formats
                item = re.sub(r'(\$\{\w+)\.\d+(\})', r'\1\2', item)
                # Do variable substitution
                result = Template(item).substitute(currentns)
                if 'num' in currentns:
                    num += 1
                namespace.clear()
                namespace.update(globals)
                yield result
                break
            except KeyError, key:
                if 'num' in namespace:
                    del namespace['num']
                continue
        else:
            break

    raise ValueError, 'Filename could not be created.'


class GeneratorProxy(object):
    def __init__(self, gen, **kwargs):
        self._gp_gen = gen
        vars(self).update(kwargs)
    def __call__(self):
        return self._gp_gen.next()
    def __getattr__(self, name):
        return getattr(self._gp_gen, name)
        

class URL(unicode):

    def relativeto(self, src):
        """
        Get the path of this URL relative to `src'
    
        """
        if isinstance(src, Node):
            src = src.url
    
        dest, src = os.path.normpath(str(self)), os.path.normpath(src)
        base = os.path.join(*(['a/'] * max(dest.count('/'), src.count('/'))))
        src = os.path.join(base, src).split('/')
        dest = os.path.join(base, dest).split('/')
    
        same = 0
        for d, s in zip(dest, src):
            if d == s:
                same += 1
                continue
            break 
    
        dest, src = dest[same:], src[same:-1]
    
        if src:
            return type(self)(os.path.join(os.path.join(*(['..'] * len(src))), 
                                           os.path.join(*dest)))

        return type(self)(os.path.join(*dest))
