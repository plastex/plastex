#!/usr/bin/env python

#from imagers.dvi2bitmap import DVI2Bitmap
from imagers.dvipng import DVIPNG

class Renderer(dict):
    def __init__(self, data={}):
        dict.__init__(self, data)
        self.imager = DVIPNG()
#       self.imager = DVI2Bitmap()
