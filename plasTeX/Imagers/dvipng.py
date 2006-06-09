#!/usr/bin/env python

import plasTeX.Imagers

class DVIPNG(plasTeX.Imagers.Imager):
    """ Imager that uses dvipng """
    command = 'dvipng -o img%d.png -D 110'
    fileextension = '.png'

Imager = DVIPNG
