#!/usr/bin/env python

#from imagers.dvi2bitmap import DVI2Bitmap
#from imagers.dvipng import DVIPNG
from StringIO import StringIO

class Renderer(dict):
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.imager = StringIO()
#       self.imager = DVIPNG()
#       self.imager = DVI2Bitmap()
