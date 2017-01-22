import os, sys

class PackageResource(object):
    outdir = ''
    copy = False
    key=''

    def __init__(self, renderers=None, package='', key='', data=None):
        self.renderers = renderers or []
        self.package = package
        self.data = data
        self.key = key or self.key

    def alterRenderer(self, renderer):
        pass

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
        rendererdir = os.path.dirname(
                sys.modules[renderer.__module__].__file__)
        renderer.importDirectory(
                os.path.join(rendererdir, self.package, self.data or ''))
