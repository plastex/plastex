#!/usr/bin/env python

import re
from DOM import DocumentFragment
from Utils import *
#from imagers.dvi2bitmap import DVI2Bitmap
#from imagers.dvipng import DVIPNG

def xmlstr(obj):
    """ Escape special characters to create a legal xml string """
    if isinstance(obj, basestring):
        return obj.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    else:
        return str(obj)

class Renderer(dict):
    def __init__(self, data={}):
        dict.__init__(self, data)
#       self.imager = DVIPNG()
#       self.imager = DVI2Bitmap()

class RenderMixIn(object):
    """
    MixIn class to make macros renderable

    """

    renderer = None

    def toXML(self):
        """ 
        Dump the object as XML 

        Returns:
        string in XML format

        """
        # Only the content of DocumentFragments get rendered
        if isinstance(self, DocumentFragment):
            s = []
            for value in self:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                else:
                    value = xmlstr(value)
                s.append(value)
            return ''.join(s)

        # Remap name into valid XML tag name
        name = self.nodeName
        name = name.replace('@','-')

        modifier = re.search(r'(\W*)$', name).group(1)
        if modifier:
            name = re.sub(r'(\W*)$', r'', name)
            modifier = ' modifier="%s"' % xmlstr(modifier)

        if not name:
            name = 'unknown'

        source = ''
        #source = ' source="%s"' % xmlstr(self.source)

        ref = ''
        if self.ref is not None:
            ref = ' ref="%s"' % xmlstr(self.ref)

        label = ''
        if self.id != id(self):
            label = ' id="%s"' % xmlstr(self.id)

        # Bail out early if the element is empty
        if not(self.attributes) and not(self.childNodes):
            return '<%s%s%s%s%s/>' % (name, modifier, source, ref, label)

        s = ['<%s%s%s%s%s>\n' % (name, modifier, source, ref, label)]
            
        # Render attributes
        if self.attributes:
            for key, value in self.attributes.items():
                if value is None:
                    s.append('    <plastex:arg name="%s"/>\n' % key)
                else:
                    if hasattr(value, 'toXML'):
                        value = value.toXML()
                    else:
                        value = xmlstr(value)
                    s.append('    <plastex:arg name="%s">%s</plastex:arg>\n' % (key, value))

        # Render content
        if self.childNodes:
            for value in self.childNodes:
                if hasattr(value, 'toXML'):
                    value = value.toXML()
                else: 
                    value = xmlstr(value)
                s.append(value)
        s.append('</%s>' % name)
        return ''.join(s)
        
    def render(self, renderer=None, file=None):
        """ 
        Render the macro 

        Keyword Arguments:
        renderer -- rendering callable to use instead of the
            one supplied by the macro itself
        file -- file write to

        Returns:
        rendered output -- if no file was specified
        nothing -- if a file was specified

        """
        # Get filename to use
        if file is None:
            file = type(self).context.renderer.filename(self)

        if file is not None:
            status.info(' [%s' % file)

        # If we have a renderer, use it
        if renderer is not None:
            output = renderer(self)

        # Use renderer associated with class
        elif type(self).renderer is not None:
            output = type(self).renderer(self)

        # No renderer, just make something up
        else:
            output = '%s' % self
#           output = ''.join([str(x) for x in self])
#           if type(self) is not TeXFragment:
#               name = re.sub(r'\W', 'W', self.tagName)
#               output = '<%s>%s</%s>' % (name, output, name)

        # Write to given file
        if file is not None:
            if hasattr(file, 'write'):
                file.write(output)
            else:
                open(file,'w').write(output)
            status.info(']')
            return ''

        # No files, just return the output
        else:
            return output

#   def __str__(self):
#       s = []
#       for child in self.childNodes:
#           if isinstance(child, basestring):
#               s.append(child)
#           else:
#               s.append(child.render())
#       return ''.join(s)

#   __repr__ = __str__
