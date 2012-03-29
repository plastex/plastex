#!/usr/bin/env python

import os, re, glob
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
            rc = os.system('dvisvgm --exact --scale=1.6 --no-fonts --output=%s --page=%d images.dvi' % (filename, page))
            if rc:
                break
            
            # dvisvgm always puts "-<page-number>" on each file.  Get rid of it. 
            try: os.rename(glob.glob(filename+'-*')[0], filename)
            except IndexError: break
            
            if not open(filename).read().strip():
                os.remove(filename)
                break
            page += 1
            if page > len(self.images):
                break
        return rc, None

Imager = DVISVGM
