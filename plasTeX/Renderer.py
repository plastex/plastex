#!/usr/bin/env python

from plasTeX.DOM import Node
from imagers.dvi2bitmap import DVI2Bitmap
from imagers.dvipng import DVIPNG
from imagers import Imager
from StringIO import StringIO
from plasTeX.Config import config
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')

encoding = config['encoding']['output']
useids = config['files']['use-ids']
ext = config['files']['extension']
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

    default = unicode
    outputtype = unicode

    def __init__(self, data={}):
        dict.__init__(self, data)

        # List of files created during rendering process
        self.files = []

        # Image generator
        if config['images']['enabled']:
            program = config['images']['program']
            if program == 'dvipng':
                self.imager = DVIPNG()
            elif program == 'dvi2bitmap':
                self.imager = DVI2Bitmap()
            else:
                log.warning('Unrecognized imager "%s"', program)
                self.imager = Imager()
        else:
            self.imager = Imager()

        # Filename generator
        self.newfilename = self._newfilename()

    def _newfilename(self):
        """ 
        Filename generator 

        """
        # Get the template and extension for output filenames
        ext = config['files']['extension']
        template = config['files'].get('template', raw=True) + ext
    
        # Return the index filename on the first pass
        yield config['files'].get('index', raw=True) + ext
    
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
        # Mix in required methods and members
        mixin(Node, Renderable)
        Node.renderer = self

        # Add document preamble to image document
        self.imager.addtopreamble(document.preamble.source)

        # Invoke the rendering process
        result = unicode(document)

        # Close imager so it can finish processing
        self.imager.close()

        # Run any cleanup activities
        self.cleanup()

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
        for key in keys:
            if self.has_key(key):
                return self[key]
        return default


class Renderable(object):

    def __unicode__(self):
        """
        Render the object and all of the child nodes

        """
        if not self.hasChildNodes():
            return u''

        r = Node.renderer
        filename = self.filename

        if filename:
            status.info(' [ %s ', filename)

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
            val = r.find(names, r.default)(child)
            if type(val) is unicode:
                s.append(val)
            else:
                s.append(unicode(val,encoding))

        if filename:
            status.info(' ] ')

        return r.outputtype(u''.join(s))

    def __str__(self):
        return unicode(self)

    def image(self):
        """ Generate an image and return the image filename """
        return Node.renderer.imager.newimage(self.source)
    image = property(image)

    def url(self):
        """
        Return the relative URL of the object

        If the object actually creates a file, just the filename will
        be returned (e.g. foo.html).  If the object is within a file, 
        both the filename and the anchor will be returned 
        (e.g. foo.html#bar).

        """
        if self.filename:
            return self.filename
        node = self.parentNode
        while node is not None and node.filename is None:
            node = node.parentNode
        filename = ''
        if node is not None:
            filename = node.filename
        return '%s#%s' % (filename, self.id)
    url = property(url)

    def filename(self):
        """
        The filename that this object should create

        Objects that don't create new files should simply return `None`.

        """
        try:
            return getattr(self, 'filenameoverride')
        except AttributeError:
            if self.level > splitlevel:
                filename = None
            elif useids and self.id != ('a%s' % id(self)):
                filename = '%s%s' % (self.id, ext)
            else:
                filename = Node.renderer.newfilename.next()
            setattr(self, 'filenameoverride', filename)
        return filename
    filename = property(filename)

