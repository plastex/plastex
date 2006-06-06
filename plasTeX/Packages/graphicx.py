#!/usr/bin/env python

import os
from plasTeX import Command

class includegraphics(Command):
    args = '[ options:dict ] file:str'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        f = self.attributes['file']
        ext = self.ownerDocument.userdata.get('packages', {}).get('graphicx', {}).get('extensions', ['.png','.jpg','.jpeg','.gif','.pdf','.ps','.eps'])
        img = None
        for e in ['']+ext:
            try: 
                img = os.path.abspath(tex.kpsewhich(f+e))
                break
            except (OSError, IOError): 
                pass 
        self.imageoverride = img
        return res

class DeclareGraphicsExtensions(Command):
    args = 'ext:list'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        ext = self.attributes['ext']
        data = self.ownerDocument.userdata
        if 'packages' not in data:
            data['packages'] = {}
        if 'graphicx' not in data['packages']:
            data['packages']['graphicx'] = {}
        self.ownerDocument.userdata['packages']['graphicx']['extensions'] = ext
        return res

class rotatebox(Command):
    args = 'angle:float self'

class scalebox(Command):
    args = 'hscale:float [ vscale:float ] self'

class reflectbox(Command):
    args = 'self'

class resizebox(Command):
    args = 'hlength:dimen vlength:dimen self'
