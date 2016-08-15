#!/usr/bin/env python

import subprocess
import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer
from plasTeX.Renderers import Renderer as BaseRenderer

class HTML5(_Renderer):
    """ Renderer for HTML5 documents, heavily copied from XHTML renderer """

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def loadTemplates(self, document):
        """Load templates as in PageTemplate but also look for packages that
        want to override some templates.""" 
        
        _Renderer.loadTemplates(self, document)
        path = os.path.join(os.path.dirname(__file__), 'pkg_override')
        for pkg in document.userdata.get('pkg_override', []):
            self.importDirectory(os.path.join(path, pkg))

    def render(self, document):
        """ Load templates and render the document """
        self.loadTemplates(document)
        BaseRenderer.render(self, document)

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

    def cleanup(self, document, files, postProcess=None):
        """
        Cleanup method called at the end of rendering.
        Uses the base renderer cleanup but calls packages callbacks before and
        after.
        """

        precleanup_cbs = document.userData.get('precleanup_cbs', [])
        for precleanup_cb in precleanup_cbs:
            precleanup_cb()

        _Renderer.cleanup(self, document, files, postProcess)

        postcleanup_cbs = document.userData.get('postcleanup_cbs', [])
        for postcleanup_cb in postcleanup_cbs:
            postcleanup_cb()


Renderer = HTML5
