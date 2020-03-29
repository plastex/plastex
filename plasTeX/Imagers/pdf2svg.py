#!/usr/bin/env python

import os
import subprocess
from plasTeX.Imagers import VectorImager

class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'

    def executeConverter(self, output):
        open('images-uncropped.pdf', 'wb').write(output)
        subprocess.call(["pdfcrop", "images-uncropped.pdf", "images.pdf"], stdout=subprocess.PIPE)

        rc = 0
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = subprocess.call(['pdf2svg', 'images.pdf', filename, str(page)], stdout=subprocess.PIPE)
            if rc:
                break

            if not open(filename).read().strip():
                os.remove(filename)
                break
            page += 1
            if page > len(self.images):
                break
        return rc, None

Imager = PDFSVG
