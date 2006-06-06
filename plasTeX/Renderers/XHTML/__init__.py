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

            # Clean up empty paragraphs and table cells
            s = re.compile(r'(<p\b[^>]*>)\s*(</p>)', re.I).sub(r'', s)
            s = re.compile(r'(<td\b[^>]*>)\s*(</td>)', re.I).sub(r'\1&nbsp;\2', s)
            
            # Add width, height, and depth to images
            s = re.compile(r'<img\b[^>]+>', re.I).sub(self.setImageData, s) 

            # Force XHTML syntax on empty tags
            s = re.compile(r'(<(?:br|img|link|meta)\b[^>]*)/?(>)', re.I).sub(r'\1 /\2', s)

            # Convert characters >127 to entities
            s = list(s)
            for i, item in enumerate(s):
                if ord(item) > 127:
                    s[i] = '&#%.3d;' % ord(item)
             
            open(f, 'w').write(unicode.encode(u''.join(s), encoding)) 

    def setImageData(self, m):
        """
        Substitute in #width, #height, and #depth parameters in image tags

        The width, height, and depth parameters aren't known until after
        all of the output has been generated.  We have to post-process
        the files to insert this information.  This method replaces
        the #width, #height, and #depth placeholders with their appropriate
        values.

        Note: #depth is actually replaced with a class name called 
              "voffset<depth>" where <depth> is the numberic value.
              In the case of negative values, the '-' is replaced 
              with '_'.

        Required Arguments:
        m -- regular expression match object that contains an img tag

        Returns:
        new image tag with width, height, and depth information

        """
        tag = m.group()

        # If the tag doesn't contain any of these, we're done
        if not re.search(r'#(width|height|depth)', tag):
            return tag

        # Get the filename
        src = re.compile(r'\bsrc\s*=\s*(\'|\")\s*([^\1]+?)\s*\1', 
                         re.I).search(tag)
        if not src:
            return tag

        src = src.group(2)

        # Make sure we have the information we need in the imager
        if not self.imager.images.has_key(src):
            return tag

        img = self.imager.images[src]

        width = img.width
        if width is None:
            width = ''

        height = img.height
        if height is None:
            height = ''

        depth = img.depth
        if depth is None:
            depth = 0

        tag = tag.replace('#width', '%spx' % width)
        tag = tag.replace('#height', '%spx' % height)
        tag = tag.replace('#depth', '%spx' % depth)

        # If we have a large descender (i.e. greater than 8px), 
        # put in this image hack to keep MSIE from truncating the 
        # image if it's within a table cell.
        if height and abs(depth) > 8: 
            tag = '%s<img src="../blank.gif" style="height:%spx" class="ieimgfix">' % (tag, height)

            # We don't want the full height to be used for the line height.
            # After some tuning, a value of (height-8px) was chosen.  That
            # seems to give decent descenders without much overlap.
            tag = '%s<span style="line-height:%spx;visibility:hidden">&#8205;</span>' % (tag, height-8)

        return tag


Renderer = XHTML 
