#!/usr/bin/env python

import os, sys
import plasTeX.Imagers.gspdfpng as gspdfpng

gs = 'gs'
if sys.platform.startswith('win'):
   gs = 'gswin32c'

class GSDVIPNG(gspdfpng.GSPDFPNG):
    """ Imager that uses gs to convert dvi to png """
    compiler = 'latex'
    verifications = ['%s --help' % gs, 'dvips --help', 'latex --help']

    def executeConverter(self, output):
        open('images.dvi', 'w').write(output)
        rc = os.system('dvips -o images.ps images.dvi')
        if rc: return rc, None
        return gspdfpng.GSPDFPNG.executeConverter(self, open('images.ps'))

Imager = GSDVIPNG
