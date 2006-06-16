#!/usr/bin/env python

import gspdfpng, os

class GSDVIPNG(gspdfpng.GSPDFPNG):
    """ Imager that uses gs to convert dvi to png """
    compiler = 'latex'
    verification = '(gs --help && dvips --help)'

    def executeconverter(self, output):
        open('images.dvi', 'w').write(output.read())
        rc = os.system('dvips -o images.ps images.dvi')
        if rc: return rc, None
        return gspdfpng.GSPDFPNG.executeconverter(self, open('images.ps'))

Imager = GSDVIPNG
