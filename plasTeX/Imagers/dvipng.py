#!/usr/bin/env python

import plasTeX.Imagers

class DVIPNG(plasTeX.Imagers.Imager):
    """ Imager that uses dvipng """
    command = 'dvipng -o img%d.png -D 120 -Q 4'
    fileExtension = '.png'

    def formatConfigOptions(self, config):
        options = []
        if config['resolution']:
            options.append(('-D', config['resolution'])) 
        return options

Imager = DVIPNG
