#!/usr/bin/env python

import subprocess, shlex
import os, shutil, re
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer
from plasTeX.Renderers import Renderer as BaseRenderer
from plasTeX.Logging import getLogger

log = getLogger()

class HTML5(_Renderer):
    """ Renderer for HTML5 documents, heavily copied from XHTML renderer """

    fileExtension = '.html'
    imageTypes = ['.svg', '.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def loadTemplates(self, document):
        """Load templates as in PageTemplate but also look for packages that
        want to override some templates and handles extra css and javascript.""" 
        
        try:
            import jinja2
        except ImportError:
            log.error('Jinja2 is not available, hence the HTML5 renderer cannot be used.')

        _Renderer.loadTemplates(self, document)
        userdata = document.userdata
        config = document.config

        rendererPath = os.path.dirname(__file__)
        overridePath = os.path.join(rendererPath, 'pkgTemplates')
        themePath = os.path.join(rendererPath, 'Theme', self.loadedTheme)

        for pkg in userdata.get('pkgTemplates', []):
            self.importDirectory(os.path.join(overridePath, pkg))

        srcDir = userdata['working-dir']
        buildDir = os.getcwd()

        # Copy all requested css files
        # Theme css has already been copied by PageTemplate.loadTemplates,
        # provided config['general']['copy-theme-extras'] is true
        try:
            os.mkdir('styles')
        except OSError:
            # This should mean the directory already exists
            pass

        pkgCssPath = os.path.join(rendererPath, 'pkgCss')
        cssBuildDir = os.path.join(buildDir, 'styles')
        
        # Start building the css list for use by the layout template
        if config['html5']['use-theme-css'] and config['general']['copy-theme-extras']:
            csss = ['theme-' + config['html5']['theme-css'] + '.css']
        else:
            csss = []

        pkgCss = userdata.get('pkgCss', [])
        for pkg in pkgCss:
            pkgPath = os.path.join(pkgCssPath, pkg)
            os.chdir(pkgPath)
            for css in sorted(os.listdir(pkgPath)):
                csss.append(css)
                shutil.copy(css, cssBuildDir)
        os.chdir(buildDir)

        os.chdir(srcDir)
        for css in config['html5']['extra-css']:
            csss.append(css)
            shutil.copy(css, cssBuildDir)
        os.chdir(buildDir)

        userdata['css'] = csss 

        # Copy all requested javascript files
        # Theme js has already been copied by PageTemplate.loadTemplates,
        # provided config['general']['copy-theme-extras'] is true
        try:
            os.mkdir('js')
        except OSError:
            pass

        pkgJsPath = os.path.join(rendererPath, 'pkgJs')
        jsBuildDir = os.path.join(buildDir, 'js')

        # Start building the js list for use by the layout template
        if config['html5']['use-theme-js'] and config['general']['copy-theme-extras']:
            jss = sorted(os.listdir(os.path.join(themePath, 'js')))
        else:
            jss = []

        pkgJs = userdata.get('pkgJs', [])
        for pkg in pkgJs:
            pkgPath = os.path.join(pkgJsPath, pkg)
            os.chdir(pkgPath)
            for js in sorted(os.listdir(pkgPath)):
                jss.append(js)
                shutil.copy(js, jsBuildDir)
        os.chdir(buildDir)

        os.chdir(srcDir)
        for js in config['html5']['extra-js']:
            jss.append(js)
            shutil.copy(js, jsBuildDir)
        os.chdir(buildDir)

        userdata['js'] = jss

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
            proc = subprocess.Popen(
                    shlex.split(filter_), 
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
        after. Callbacks should be listed in
        document.userdata['preCleanupCallbacks']
        or document.userdata['postCleanupCallbacks']. Each call back should accept the
        current document as its only argument. Pre-cleanup call back must return
        the list of path of files they created (relative to the output directory).
        """

        preCleanupCallbacks = document.userdata.get('preCleanupCallbacks', [])
        for preCleanupCallback in preCleanupCallbacks:
            files += preCleanupCallback(document)

        _Renderer.cleanup(self, document, files, postProcess)


Renderer = HTML5
