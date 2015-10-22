#!/usr/bin/env python

import os
import re
import subprocess

import plasTeX.Imagers

class pdftoppm(plasTeX.Imagers.Imager):
    """ Imager that uses libpoppler's pdftoppm to convert pdf to png """
    command = 'pdftoppm -png -r 150'
    compiler = 'pdflatex'
    fileExtension = '.png'

    def verify(self):
        """
        pdftoppm writes its help message to standard error, and not
        standard output as plasTeX expects, and we thus have to
        override this method. Note that this method will also work if
        pdftoppm writes its help message to standard output.

        """
        cmd = self.command.split()[0]
        proc = subprocess.Popen('%s --help' % cmd, 
                                shell=True, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        return 'pdftoppm' in str(proc.communicate())

    def executeConverter(self, output):
        """ 
        We need to override this because plasTeX always puts the input
        file at the end of the command-line.  We also need to return the
        list of images.
        
        """
        open('images.out', 'wb').write(output.read())
        options = ''
        if self._configOptions:
            for opt, value in self._configOptions:
                opt, value = str(opt), str(value)
                if ' ' in value:
                    value = '"%s"' % value
                options += '%s %s ' % (opt, value)
        rc = os.system('%s %s%s img' % (self.command, options, 'images.out'))
        return rc, [f for f in os.listdir('.') if re.match(r'^img-\d+\.\w+$', f)]
    
Imager = pdftoppm
