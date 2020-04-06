#!/usr/bin/env python

import os
from plasTeX.Imagers import VectorImager as _Imager

class DVISVGM(_Imager):
    """ Imager that uses dvisvgm """
    fileExtension = '.svg'
    verifications = ['dvisvgm --help', 'latex --help']
    compiler = 'latex'

    def executeConverter(self, output):
        rc = 0
        open('images.dvi', 'wb').write(output)
        scale = self.config["images"]["scale-factor"]
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = os.system('dvisvgm --exact --scale={} --no-fonts --output={} --page={} images.dvi'.format(scale, filename, page))
            if rc:
                break

            # dvisvgm always puts "-<page-number>" on each file.  Get rid of it.
#            try:
#                os.rename(glob.glob(filename+'-*')[0], filename)
#            except IndexError:
#                break

            if not open(filename).read().strip():
                os.remove(filename)
                break
            page += 1
            if page > len(self.images):
                break
        return rc, None

Imager = DVISVGM
