#!/usr/bin/env python

from plasTeX.DOM import Node
#from imagers.dvi2bitmap import DVI2Bitmap
#from imagers.dvipng import DVIPNG
from StringIO import StringIO
from plasTeX.Config import config

encoding = config['encoding']['output']
useids = config['filenames']['use-ids']
ext = config['filenames']['extension']

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
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.imager = StringIO()
#       self.imager = DVIPNG()
#       self.imager = DVI2Bitmap()
        self.filenames = self._filenames()

    def _filenames(self):
        """ Filename generator """
        # Get the template and extension for output filenames
        ext = config['filenames']['extension']
        template = config['filenames'].get('template', raw=True) + ext
    
        # Return the index filename on the first pass
        yield config['filenames'].get('index', raw=True) + ext
    
        # Generate new filenames
        v = {'num':1}
        while 1:
            yield template % v
            v['num'] += 1

    def applyto(self, context):
        # Shove the Renderable Mixin into the Macro base classes
        mixin(Node, Renderable)
        Node.renderer = self
        macros = context.globals()
        for key, value in macros.items():
            value.render = self.get(key, unicode) 


class Renderable(object):

    renderer = None
    render = unicode

    def __unicode__(self):
        if not self.hasChildNodes():
            return u''
        s = []
        for child in self.childNodes:
            val = type(child).render(child)
            if type(val) is unicode:
                s.append(val)
            else:
                s.append(unicode(val,encoding))
        return u''.join(s)

    def __str__(self):
        return unicode(self)

    def image(self):
        return self.renderer.imager.newimage(self.source)
    image = property(image)

    def url(self):
        if self.filename:
            return self.filename
        return '%s#%s' % (self.filename, self.id)
    url = property(url)

    def filename(self):
        try:
            return getattr(self, '@filename')
        except AttributeError:
            if self.level > Node.ENDSECTIONS_LEVEL:
                filename = None
            elif useids and self.id != id(self):
                filename = '%s%s' % (self.id, ext)
            else:
                filename = self.renderer.filenames.next()
            setattr(self, '@filename', filename)
        return filename
    filename = property(filename)

