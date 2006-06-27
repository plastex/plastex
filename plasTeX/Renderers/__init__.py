#!/usr/bin/env python

import codecs, os, shutil, string
from plasTeX.Filenames import Filenames
from plasTeX.DOM import Node
from plasTeX.Logging import getLogger
from plasTeX.Imagers import Image, PILImage

log = getLogger()
status = getLogger('status')

import logging
logging.getLogger('simpleTAL').setLevel(logging.WARNING)
logging.getLogger('simpleTALES').setLevel(logging.WARNING)

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
        if item in ['__dict__','__module__','__doc__','__weakref__']:
            continue
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
    imagetypes = []
    vectorimagetypes = []
    fileextension = ''
    imageattrs = '&${filename}-${attr};'
    imageunits = '&${units};'

    def __init__(self, data={}):
        dict.__init__(self, data)

        # Names of generated files
        self.files = {}

        # Instantiated at render time
        self.imager = None
        self.vectorimager = None

        # Filename generator
        self.newfilename = None

    def render(self, document):
        """
        Invoke the rendering process

        This method invokes the rendering process as well as handling
        the setup and shutdown of image processing.

        Required Arguments:
        document -- the document object to render

        """
        config = document.config

        # If there are no keys, print a warning.  
        # This is most likely a problem.
        if not self.keys():
            log.warning('There are no keys in the renderer.  ' +
                        'All objects will use the default rendering method.')

        # Mix in required methods and members
        mixin(Node, Renderable)
        Node.renderer = self

        # Create a filename generator
        self.newfilename = Filenames(config['files'].get('filename', raw=True), 
                                     (config['files']['bad-chars'],
                                      config['files']['bad-chars-sub']),
                                     {'jobname':document.userdata.get('jobname', '')}, self.fileextension)
                      

        # Instantiate appropriate imager
        names = [x for x in config['images']['imager'].split() if x]
        for name in names:
            if name == 'none':
                break
            try: 
                exec('from plasTeX.Imagers.%s import Imager' % name)
            except ImportError, msg:
                log.warning("Could not load imager '%s' because '%s'" % (name, msg))
                continue
            
            self.imager = Imager(document)
    
            # Make sure that this imager works on this machine
            if self.imager.verify():
                break
 
            self.imager = None

        # Still no imager? Just use the default.
        if self.imager is None:
            if 'none' not in names:
                log.warning('Could not find a valid imager in the list: %s.  The default imager will be used.' % ', '.join(names))
            from plasTeX.Imagers import Imager
            self.imager = Imager(document)

        if self.imagetypes and self.imager.fileextension not in self.imagetypes:
            self.imager.fileextension = self.imagetypes[0]
        if self.imageattrs and not self.imager.imageattrs:
            self.imager.imageattrs = self.imageattrs
        if self.imageunits and not self.imager.imageunits:
            self.imager.imageunits = self.imageunits

        # Instantiate appropriate vector imager
        names = [x for x in config['images']['vector-imager'].split() if x]
        for name in names:
            if name == 'none':
                break
            try: 
                exec('from plasTeX.Imagers.%s import Imager' % name)
            except ImportError, msg:
                log.warning("Could not load imager '%s' because '%s'" % (name, msg))
                continue
            
            self.vectorimager = Imager(document)
    
            # Make sure that this imager works on this machine
            if self.vectorimager.verify():
                break
 
            self.vectorimager = None

        # Still no vector imager? Just use the default.
        if self.vectorimager is None:
            if 'none' not in names:
                log.warning('Could not find a valid vector imager in the list: %s.  The default vector imager will be used.' % ', '.join(names))
            from plasTeX.Imagers import VectorImager
            self.vectorimager = VectorImager(document)

        if self.vectorimagetypes and \
           self.vectorimager.fileextension not in self.vectorimagetypes:
            self.vectorimager.fileextension = self.vectorimagetypes[0]
        if self.imageattrs and not self.vectorimager.imageattrs:
            self.vectorimager.imageattrs = self.imageattrs
        if self.imageunits and not self.vectorimager.imageunits:
            self.vectorimager.imageunits = self.imageunits


        # Invoke the rendering process
        unicode(document)

        # Finish rendering images
        self.imager.close()
        self.vectorimager.close()

        # Run any cleanup activities
        self.cleanup(document, self.files.values())

        # Remove mixins
        del Node.renderer
        unmix(Node, Renderable)

    def processFileContent(self, document, s):
        return s

    def cleanup(self, document, files):
        """ 
        Cleanup method called at the end of rendering 

        This method allows you to do arbitrary post-processing after
        all files have been rendered.

        Note: While I greatly dislike post-processing, sometimes it's 
              just easier...

        Required Arguments:
        document -- the document being rendered

        """
        if self.processFileContent is Renderer.processFileContent:
            return 

        encoding = document.config['files']['output-encoding']

        for f in files:
            try:
                s = codecs.open(str(f), 'r', encoding).read()
            except IOError, msg:
                log.error(msg)
                continue

            s = self.processFileContent(document, s)

            codecs.open(f, 'w', encoding).write(u''.join(s))

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

        # Other nodes supplied default
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
        r = Node.renderer

        # Short circuit macros that have unicode equivalents
        uni = self.unicode
        if uni is not None: 
            return r.outputtype(r.textdefault(uni))

        # If we don't have childNodes, then we're done
        if not self.hasChildNodes():
            return u''

        if self.filename:
            status.info(' [ %s ', self.filename)

        # At the very top level, only render the DOCUMENT_LEVEL node
        if self.nodeType == Node.DOCUMENT_NODE:
            childNodes = [x for x in self.childNodes 
                            if x.level == Node.DOCUMENT_LEVEL]
        else:
            childNodes = self.childNodes

        # Render all child nodes
        s = []
        for child in childNodes:

            # Short circuit text nodes
            if child.nodeType == Node.TEXT_NODE:
                s.append(r.textdefault(child))
                continue

            # Short circuit macros that have unicode equivalents
            uni = child.unicode
            if uni is not None: 
                s.append(r.textdefault(uni))
                continue

            layouts, names = [], []
            nodeName = child.nodeName
            modifier = None

            # Does the macro have a modifier (i.e. '*')
            if child.attributes:
                modifier = child.attributes.get('*modifier*')

            if child.filename:
                # Filename and modifier
                if modifier:
                    layouts.append('%s-layout%s' % (nodeName, modifier))

                # Filename only
                layouts.append('%s-layout' % nodeName)

            # Modifier only
            if modifier:
                names.append('%s%s' % (nodeName, modifier))

            names.append(nodeName)
            layouts.append('default-layout')

            # Locate the rendering callable, and call it with the 
            # current object (i.e. `child`) as its argument.
            val = r.find(names, r.default)(child)

            # If a plain string is returned, we have no idea what 
            # the encoding is, but we'll make a guess.
            if type(val) is not unicode:
                log.warning('The renderer for %s returned a non-unicode string.  Using the default input encoding.' % type(child).__name__)
                val = unicode(val, child.config['files']['input-encoding'])

            # If the content should go to a file, write it and go
            # to the next child.
            if child.filename:
                filename = child.filename

                # Create any directories as needed
                directory = os.path.dirname(filename)
                if directory and not os.path.isdir(directory):
                    os.makedirs(directory)

                # Add the layout wrapper if there is one
                func = r.find(layouts)
                if func is not None:
                    val = func(StaticNode(child, val))

                    # If a plain string is returned, we have no idea what 
                    # the encoding is, but we'll make a guess.
                    if type(val) is not unicode:
                        log.warning('The renderer for %s returned a non-unicode string.  Using the default input encoding.' % type(child).__name__)
                        val = unicode(val, child.config['files']['input-encoding'])

                # Write the file content
                codecs.open(filename, 'w', child.config['files']['output-encoding']).write(val)

                continue

            # Append the resultant unicode object to the output
            s.append(val)

        if self.filename:
            status.info(' ] ')

        return r.outputtype(u''.join(s))

    def __str__(self):
        return unicode(self)

    @property
    def image(self):
        """ Generate an image and return the image filename """
        return Node.renderer.imager.getimage(self)

    @property
    def vectorimage(self):
        """ Generate a vector image and return the image filename """
        image = Node.renderer.vectorimager.getimage(self)
        image.bitmap = Node.renderer.imager.getimage(self)
        return image

    @property
    def url(self):
        """
        Return the relative URL of the object

        If the object actually creates a file, just the filename will
        be returned (e.g. foo.html).  If the object is within a file, 
        both the filename and the anchor will be returned 
        (e.g. foo.html#bar).

        """
        base = self.config['document']['base-url']
        if base and base.endswith('/'):
            base = base[:-1]
        
        # If this generates a file, return that filename
        if self.filename:
            if base:
                return URL('%s/%s' % (base, self.filename))
            return URL(self.filename)

        # If this is a location within a file, return that location
        node = self.parentNode
        while node is not None and node.filename is None:
            node = node.parentNode
        filename = ''
        if node is not None:
            filename = node.filename
        if base:
            return URL('%s/%s#%s' % (base, filename, self.id))
        return URL('%s#%s' % (filename, self.id))

    @property
    def filename(self):
        """
        The filename that this object should create

        Objects that don't create new files should simply return `None`.

        """
        r = Node.renderer

        try: return r.files[self]
        except KeyError: pass

        try:
            if self.filenameoverride:
                userdata = self.ownerDocument.userdata
                config = self.ownerDocument.config
                newfilename = Filenames(self.filenameoverride,
                                        (config['files']['bad-chars'],
                                         config['files']['bad-chars-sub']),
                                        {'jobname':userdata.get('jobname','')},
                                        self.fileextension)
                filename = r.files[self] = newfilename()
                return filename

        except AttributeError:
            if not hasattr(self, 'config'):
                return

            # If our level doesn't invoke a split, don't return a filename
            if self.level > self.config['files']['split-level']:
                return

            # Populate vars of filename generator
            # and call the generator to get the filename.
            ns = r.newfilename.vars
            if hasattr(self, 'id') and self.id != ('a%s' % id(self)):
                ns['id'] = self.id
            if hasattr(self, 'title'):
                if hasattr(self.title, 'textContent'):
                    ns['title'] = self.title.textContent
                elif isinstance(self.title, basestring):
                    ns['title'] = self.title
            r.files[self] = filename = r.newfilename()

        return filename


class StaticNode(object):
    """
    Object to assist in rendering files

    This object is used to wrap objects that need to have a layout
    file wrapped around them.  The layout wrapper generally includes 
    all of the navigation links, table of contents, etc.  

    This is simply a proxy object that returns the attributes of
    the given object.  The exceptions are __unicode__ and __str__
    which simply return the rendered string that was passed in.
    This allows you to use two templates: one that renders the content
    and another that is wrapped around any node that generates a 
    file.  Without this, you can easily run into infinite recursion 
    problems.

    """
    def __init__(self, obj, content):
        """
        Initialize the static node

        Arguments:
        obj -- the object that contains navigation and table of 
            contents information
        content -- the rendered object in a unicode string

        """
        self._node_data = (obj, content)
    def __getattribute__(self, name):
        if name in ['_node_data','__unicode__','__str__']:
            return object.__getattribute__(self, name)
        return getattr(self._node_data[0], name)
    def __unicode__(self):
        return self._node_data[1]
    def __str__(self):
        return unicode(self)


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
