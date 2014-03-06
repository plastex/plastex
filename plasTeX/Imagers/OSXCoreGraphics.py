#!/usr/bin/env python

import plasTeX.Imagers

class CoreGraphics(plasTeX.Imagers.Imager):
    """ Imager that uses OS X's CoreGraphics library """
    command = 'cgpdfpng --magnification=6 --scaledown=4 --output=img%d.png'
    compiler = 'pdflatex'
    fileExtension = '.png'

Imager = CoreGraphics
