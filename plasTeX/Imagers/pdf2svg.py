#!/usr/bin/env python

from pathlib import Path
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

    def executeConverter(self, output: bytes) -> Tuple[int, Optional[List[str]]]:
        Path("images-uncropped.pdf").write_bytes(output)

        subprocess.call(["pdfcrop", "images-uncropped.pdf", "images.pdf"], stdout=subprocess.DEVNULL)

        rc = 0
        for page in range(1, len(self.images) + 1):
            filename = 'img%d.svg' % page
            rc = subprocess.call(['pdf2svg', 'images.pdf', filename, str(page)], stdout=subprocess.DEVNULL)
            if rc:
                break

            scale = self.config["images"]["scale-factor"]
            if scale != 1:
                tree = ET.parse(filename)
                root = tree.getroot()

                for attrib in ["width", "height"]:
                    m = length_re.match(root.attrib[attrib])
                    root.attrib[attrib] = "{:.2f}{}".format(float(m.group(1)) * scale, m.group(2))

                tree.write(filename)

        return rc, None

Imager = PDFSVG
