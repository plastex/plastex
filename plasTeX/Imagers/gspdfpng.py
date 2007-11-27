#!/usr/bin/env python

from plasTeX.Logging import getLogger
import plasTeX.Imagers, glob, sys

status = getLogger('status')

gs = 'gs'
if sys.platform.startswith('win'):
   gs = 'gswin32c'

class GSPDFPNG(plasTeX.Imagers.Imager):
    """ Imager that uses gs to convert pdf to png """
    command = ('%s -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m -r250 ' % gs) + \
              '-dGraphicsAlphaBits=4 -sOutputFile=img%d.png'
    compiler = 'pdflatex'
    fileExtension = '.png'

    def executeConverter(self, output):
        res = plasTeX.Imagers.Imager.executeConverter(self, output)
        self.scaleImages()
        return res

    def scaleImages(self):
        """ Scale images down and anti-alias """
        if plasTeX.Imagers.PILImage is not None:
            PILImage = plasTeX.Imagers.PILImage
            scaledown = 2.2
            for filename in glob.glob('img*.png'):
                status.info('[%s]' % filename,)
                img = plasTeX.Imagers.autoCrop(PILImage.open(filename), 
                                               margin=3)[0]
                width, height = [int(float(x)/scaledown) for x in img.size]
                img = img.resize((width, height), PILImage.ANTIALIAS)
                img = img.point(self.toWhite)
                img.save(filename)

    def toWhite(self, pixel):
        if pixel >= 245:
            return 255
        return pixel

    def formatConfigOptions(self, config):
        options = []
        if config['resolution']:
            options.append(('-r%s' % config['resolution'], '')) 
        return options

Imager = GSPDFPNG
