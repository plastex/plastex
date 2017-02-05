import os, inspect, re, shutil

from plasTeX.Logging import getLogger

log = getLogger()

def rendererDir(renderer):
    """Convenience wrapper around inspect.getfile to get the renderer
    directory"""
    return os.path.dirname(inspect.getfile(renderer.__class__))

class PackageResource(object):
    outdir = ''
    copy = False
    key=''

    def __init__(self, renderers=None, package='', key='', data=None):
        if isinstance(renderers, list):
            self.rendererPatterns = renderers
        else:
            self.rendererPatterns = [renderers]
        self.package = package
        self.data = data
        self.key = key or self.key
        self.workingdir = ''

    def alter(self, renderer=None, rendererName='', document=None, target=''):
        doIt = False
        for pattern in self.rendererPatterns:
            if re.match(pattern, rendererName):
                doIt = True
                break
        if doIt:
            self.workingdir = document.userdata.get('working-dir', '')
            self.alterRenderer(renderer)
            self.alterDocument(document=document, rendererName=rendererName)
            self.copyFile(renderer=renderer, target=target)

    def alterRenderer(self, renderer):
        pass

    def alterDocument(self, document=None, rendererName=''):
        rendererdata = document.rendererdata[rendererName]
        if self.key:
            if isinstance(self.data, list):
                data = self.data
            else:
                data = [self.data]
            rendererdata.setdefault(self.key, []).extend(data)

    def copyFile(self, renderer=None, target=None):
        if self.copy and renderer and target:
            rendererdir = rendererDir(renderer)
            source = os.path.join(self.workingdir, self.package, self.data)
            try:
                shutil.copy(
                        source,
                        os.path.join(target, self.outdir))
            except IOError:
                source = os.path.join(rendererdir, self.package, self.data)
                try:
                    shutil.copy(
                            source,
                            os.path.join(target, self.outdir))
                except IOError:
                    log.error('Package resource file not found :'+source)


class PackageCss(PackageResource):
    outdir = 'styles'
    key = 'css'
    copy = True

class PackageJs(PackageResource):
    outdir = 'js'
    key = 'js'
    copy = True

class PackageTemplateDir(PackageResource):
    def alterRenderer(self, renderer):
        rendererdir = rendererDir(renderer)
        subdir = os.path.join(self.package, self.data or '')
        userpath = os.path.join(self.workingdir, subdir)
        rendererpath = os.path.join(rendererdir, subdir)
        if os.path.isdir(userpath):
            renderer.importDirectory(userpath)
        elif os.path.isdir(rendererpath):
            renderer.importDirectory(rendererpath)
        else:
            log.error('Package template directory not found :' + subdir)
