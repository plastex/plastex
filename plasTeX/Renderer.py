#!/usr/bin/env python

from plasTeX.DOM import Node
from imagers.dvi2bitmap import DVI2Bitmap
from imagers.dvipng import DVIPNG
from imagers import Imager
from StringIO import StringIO
from plasTeX.Config import config
from plasTeX.Logging import getLogger
import codecs

log = getLogger()
status = getLogger('status')

encoding = config['files']['output-encoding']
useids = config['files']['use-ids']
filetemplate = config['files'].get('filename', raw=True)
splitlevel = config['files']['split-level']

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

    default = unicode
    outputtype = unicode

    def __init__(self, data={}):
        dict.__init__(self, data)

        # List of files created during rendering process
        self.files = []

        # Image generator
        program = config['images']['program']
        if program == 'dvipng':
            self.imager = DVIPNG()
        elif program == 'dvi2bitmap':
            self.imager = DVI2Bitmap()
        else:
            if config['images']['enabled']:
                log.warning('Unrecognized imager "%s"', program)
            self.imager = Imager()

        # Filename generator
        self.newfilename = self._newfilename()

        # Call the initialization hook
        self.initialize()

    def initialize(self):
        """ Invoke any setup that needs to be done before rendering """
        pass

    def _newfilename(self):
        """ 
        Filename generator 

        This method generates a new unique filename each time it is 
        called.  It's behavior can be modified by the files:extension
        and files:template configuration options.  The first time this
        method is called, the index filename is returned (configured
        using the files:index configuration option).

        Returns:
        unique filename

        """
        # Get the template and extension for output filenames
        basename = config['files'].get('basename', raw=True)
        template = filetemplate % {'basename':basename}
    
        # Return the index filename on the first pass
        yield filetemplate % {'basename':config['files'].get('index', raw=True)}
    
        # Generate new filenames
        v = {'num':1}
        while 1:
            yield template % v
            v['num'] += 1

    def render(self, document):
        """
        Invoke the rendering process

        This method invokes the rendering process as well as handling
        the setup and shutdown of image processing.

        Required Arguments:
        document -- the document object to render

        """
        # If there are no keys, print a warning.  
        # This is most likely a problem.
        if not self.keys():
            log.warning('There are no keys in the renderer.  All objects will use the default rendering method.')

        # Mix in required methods and members
        mixin(Node, Renderable)
        Node.renderer = self

        # Add document preamble to image document
        self.imager.addtopreamble(document.preamble.source)

        # Invoke the rendering process
        result = unicode(document)

        # There were no files created, so create one and write the 
        # content to it.
        if not self.files:
            log.warning('No files were generated.  A file will be created that contains the result of this entire rendering.  This may produce unexpected results.')
            filename = Node.renderer.newfilename.next()
            status.info(' [ %s ] ', filename)
            self.write(filename, unicode.encode(result, encoding)) 

        # Close imager so it can finish processing
        self.imager.close()

        # Run any cleanup activities
        self.cleanup(document)

        # Remove mixins
        del Node.renderer
        unmix(Node, Renderable)

        return result

    def write(self, outputfile, content):
        """ Write `content` to file `outputfile` """
        open(outputfile, 'w').write(content)
        self.files.append(outputfile)

    def cleanup(self):
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

        if ''.join(keys) != '#text':
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

            # Append the resultant unicode object to the output
            if type(val) is unicode:
                s.append(val)
            else:
                s.append(unicode(val,encoding))

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
            return self.filename

        # If this is a location within a file, return that location
        node = self.parentNode
        while node is not None and node.filename is None:
            node = node.parentNode
        filename = ''
        if node is not None:
            filename = node.filename
        return '%s#%s' % (filename, self.id)

    @property
    def filename(self):
        """
        The filename that this object should create

        Objects that don't create new files should simply return `None`.

        """
        try:
            return getattr(self, 'filenameoverride')

        except AttributeError:
            # If our level doesn't invoke a split, don't return a filename
            if self.level > splitlevel:
                filename = None

            # Should we use LaTeX ids as filenames?
            elif useids and self.id != ('a%s' % id(self)):
                filename = filetemplate % {'basename':self.id}

            # All other cases get a generated filename
            else:
                filename = Node.renderer.newfilename.next()

            # Remove evil characters from the filename
            if filename:
                good = config['files']['bad-chars-sub']
                for char in config['files']['bad-chars']:
                    filename = filename.replace(char, good)

            # Store the name if this method is called again
            setattr(self, 'filenameoverride', filename)

        return filename

