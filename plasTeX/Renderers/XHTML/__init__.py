#!/usr/bin/env python

import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.ZPT import ZPT

log = plasTeX.Logging.getLogger()

class XHTML(ZPT):
    """ Renderer for XHTML documents """

    def cleanup(self, document, files):
        """ 
        Cleanup method called at the end of rendering 

        This method allows you to do arbitrary post-processing after
        all files have been rendered.

        Note: While I greatly dislike post-processing, sometimes it's 
              just easier...

        Required Arguments:
        document -- the document being rendered

        """
        encoding = document.config['files']['output-encoding']

        for f in files:
            try:
                s = codecs.open(str(f), 'r', encoding).read()
            except IOError, msg:
                print os.getcwd()
                log.error(msg)
                continue

            # Clean up empty paragraphs
#           s = re.compile(r'(<p\b[^>]*>)\s*(</p>)', re.I).sub(r'', s)
            
            # Add width, height, and depth to images
            s = re.sub(r'&amp;(\S+)-(width|height|depth);', self.setImageData, s) 

            # Force XHTML syntax on empty tags
#           s = re.compile(r'(<(?:br|img|link|meta)\b[^>]*)/?(>)', re.I).sub(r'\1 /\2', s)

            # Convert characters >127 to entities
#           s = list(s)
#           for i, item in enumerate(s):
#               if ord(item) > 127:
#                   s[i] = '&#%.3d;' % ord(item)
             
            open(f, 'w').write(unicode.encode(u''.join(s), encoding)) 

    def setImageData(self, m):
        """
        Substitute in width, height, and depth parameters in image tags

        The width, height, and depth parameters aren't known until after
        all of the output has been generated.  We have to post-process
        the files to insert this information.  This method replaces
        the &filename-width;, &filename-height;, and &filename-depth; 
        placeholders with their appropriate values.

        Required Arguments:
        m -- regular expression match object that contains the filename
            and the parameter: width, height, or depth.

        Returns:
        replacement for entity

        """
        filename, parameter = m.group(1), m.group(2)

        try:
            img = self.imager.images[filename]
            if getattr(img, parameter) is not None:
                return '%spx' % getattr(img, parameter)
        except KeyError: pass

        return '&%s-%s;' % (filename, parameter)

Renderer = XHTML 
