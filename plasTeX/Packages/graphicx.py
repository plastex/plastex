#!/usr/bin/env python

import os
from plasTeX import Command

from graphics import DeclareGraphicsExtensions

class includegraphics(Command):
    args = '[ options:dict ] file:str'
    packageName = 'graphicx'

    def invoke(self, tex):
        res = Command.invoke(self, tex)

        f = self.attributes['file']

        ext = self.ownerDocument.userdata.get('packages', {}).get(self.packageName, {}).get('extensions', ['.png','.jpg','.jpeg','.gif','.pdf','.ps','.eps'])
        img = None
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
                self.style['height'] = tex.castString(height)

            width = options.get('width')
            if width is not None:
                self.style['width'] = tex.castString(width)

        self.imageoverride = img

        return res
