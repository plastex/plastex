#!/usr/bin/env python

import os, re
import plasTeX.Imagers

class DVISVGM(plasTeX.Imagers.VectorImager):
    """ Imager that uses dvisvgm """
    fileExtension = '.svg'
    verification = 'dvisvgm --help'
    compiler = 'latex'

    def executeConverter(self, output):
        rc = 0
        open('images.dvi', 'w').write(output.read())
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = os.system('dvisvgm --scale=1.6 --output=%s --page=%d images.dvi' % (filename, page))
            if rc:
                break
            if not open(filename).read().strip():
                os.remove(filename)
                break
            page += 1
        return rc, None

Imager = DVISVGM
