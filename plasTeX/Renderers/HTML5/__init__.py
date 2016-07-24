#!/usr/bin/env python

import subprocess
import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class HTML5(_Renderer):
    """ Renderer for HTML5 documents, heavily copied from XHTML renderer """

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Remove empty paragraphs
        s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Add a non-breaking space to empty table cells
        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)

        for fun in document.userdata.get('processFileContents', []):
            s = fun(document, s)

        filters = document.config['html5']['filters']
        for filter_ in filters:
            print('Running ' + filter_)
            proc = subprocess.Popen(
                    filter_, 
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE)
            output, output_err = proc.communicate(s.encode(encoding="utf-8"))
            if not output_err:
                s = output.decode(encoding="utf-8")

        return s


Renderer = HTML5
