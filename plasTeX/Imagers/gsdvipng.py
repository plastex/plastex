#!/usr/bin/env python

import gspdfpng, os, sys

gs = 'gs'
if sys.platform.startswith('win'):
   gs = 'gswin32c'

class GSDVIPNG(gspdfpng.GSPDFPNG):
    """ Imager that uses gs to convert dvi to png """
    compiler = 'latex'
    verification = '(%s --help && dvips --help)' % gs

    def executeConverter(self, output):
        open('images.dvi', 'w').write(output.read())
        rc = os.system('dvips -o images.ps images.dvi')
        if rc: return rc, None
        return gspdfpng.GSPDFPNG.executeConverter(self, open('images.ps'))

Imager = GSDVIPNG
