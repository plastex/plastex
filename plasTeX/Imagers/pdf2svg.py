#!/usr/bin/env python

import subprocess
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional
from plasTeX.Imagers import VectorImager

length_re = re.compile('([0-9\\.]*)(.*)')
class PDFSVG(VectorImager):
    """ Imager that uses pdf2svg """
    fileExtension = '.svg'
    verifications = ['pdflatex --help', 'which pdf2svg', 'pdfcrop --help']
    compiler = 'pdflatex'

    def executeConverter(self, outfile=None) -> List[Tuple[str, str]]:
        if outfile is None:
            outfile = "images.pdf"

        subprocess.call(["pdfcrop", outfile, "images-cropped.pdf"], stdout=subprocess.DEVNULL)

        scale = self.config["images"]["scale-factor"]

        images = []
        for no, line in enumerate(open("images.csv")):
            filename = 'img%d.svg' % no
            page, output = line.split(",")
            images.append([filename, output.rstrip()])

            subprocess.run(['pdf2svg', 'images-cropped.pdf', filename, str(page)], stdout=subprocess.DEVNULL, check=True)

            if scale != 1:
                tree = ET.parse(filename)
                root = tree.getroot()

                for attrib in ["width", "height"]:
                    m = length_re.match(root.attrib[attrib])
                    root.attrib[attrib] = "{:.2f}{}".format(float(m.group(1)) * scale, m.group(2))

                tree.write(filename)

        return images

Imager = PDFSVG
