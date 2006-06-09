#!/usr/bin/env python

import plasTeX.Imagers

class GSPDFPNG(plasTeX.Imagers.Imager):
    """ Imager that uses gs to convert pdf to png """
    command = 'gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r130 -dGraphicsAlphaBits=4 -sOutputFile=img%d.png'
    compiler = 'pdflatex'
    fileextension = '.png'

Imager = GSPDFPNG
