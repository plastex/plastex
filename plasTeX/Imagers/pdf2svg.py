#!/usr/bin/env python

import subprocess
import re
import xml.etree.ElementTree as ET
from plasTeX.Imagers import VectorImager

length_re = re.compile('([0-9\\.]*)(.*)')
class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'

    def executeConverter(self, output):
        open('images-uncropped.pdf', 'wb').write(output)
        subprocess.call(["pdfcrop", "images-uncropped.pdf", "images.pdf"], stdout=subprocess.DEVNULL)

        rc = 0
        page = 1
        while 1:
            filename = 'img%d.svg' % page
            rc = subprocess.call(['pdf2svg', 'images.pdf', filename, str(page)], stdout=subprocess.DEVNULL)
            if rc:
                break

            scale = self.config["images"]["scale-factor"]
            if scale != 1:
                tree = ET.parse(filename)
                root = tree.getroot()

                width = length_re.match(root.attrib["width"])
                root.attrib["width"] = "{}{}".format(float(width.group(1)) * scale, width.group(2))

                height = length_re.match(root.attrib["height"])
                root.attrib["height"] = "{}{}".format(float(height.group(1)) * scale, height.group(2))

                tree.write(filename)


            page += 1
            if page > len(self.images):
                break
        return rc, None

Imager = PDFSVG
