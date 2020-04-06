#!/usr/bin/env python

import subprocess
from pathlib import Path
from plasTeX.Imagers import VectorImager as _Imager
from typing import List, Tuple, Optional

class DVISVGM(_Imager):
    """ Imager that uses dvisvgm """
    fileExtension = '.svg'
    verifications = ['dvisvgm --help', 'latex --help']
    compiler = 'latex'

    def executeConverter(self, output: bytes) -> Tuple[int, Optional[List[str]]]:
        Path('images.dvi').write_bytes(output)

        scale = self.config["images"]["scale-factor"]
        rc = 0
        for page in range(1, len(self.images) + 1):
            out = Path('img{}.svg'.format(page))

            rc = subprocess.call([
                "dvisvgm",
                "--exact",
                "--scale={}".format(scale),
                "--no-fonts",
                "--output={}".format(out),
                "--page={}".format(page),
                "images.dvi"
            ], stdout=subprocess.DEVNULL)

            if rc:
                break

            if not out.read_text().strip():
                out.unlink()
                break

        return rc, None

Imager = DVISVGM
