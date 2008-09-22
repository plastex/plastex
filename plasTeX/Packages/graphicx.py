#!/usr/bin/env python

import os
from plasTeX import Command

from graphics import DeclareGraphicsExtensions, graphicspath

class includegraphics(Command):
    args = '* [ options:dict ] file:str'
    packageName = 'graphicx'
    captionable = True

    def invoke(self, tex):
        res = Command.invoke(self, tex)

        f = self.attributes['file']
        ext = self.ownerDocument.userdata.getPath(
                      'packages/%s/extensions' % self.packageName, 
                      ['.png','.jpg','.jpeg','.gif','.pdf','.ps','.eps'])
        paths = self.ownerDocument.userdata.getPath(
                        'packages/%s/paths' % self.packageName, ['.'])
        img = None

        # Check for file using graphicspath
        for p in paths:
            for e in ['']+ext:
                fname = os.path.join(p,f+e)
                if os.path.isfile(fname):
                    img = os.path.abspath(fname)
                    break
            if img is not None:
                break

        # Check for file using kpsewhich
        if img is None:
            for e in ['']+ext:
                try: 
                    img = os.path.abspath(tex.kpsewhich(f+e))
                    break
                except (OSError, IOError): 
                    pass 

        options = self.attributes['options']

        if options is not None:

            height = options.get('height')
            if height is not None:
                self.style['height'] = height

            width = options.get('width')
            if width is not None:
                self.style['width'] = width

        self.imageoverride = img

        return res

class DeclareGraphicsExtensions(DeclareGraphicsExtensions):
    packageName = 'graphicx'

class graphicspath(graphicspath):
    packageName = 'graphicx'
