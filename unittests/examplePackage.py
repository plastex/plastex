from pathlib import Path
from plasTeX.PackageResource import (
        PackageCss, PackageJs, PackageTemplateDir,
        PackagePreCleanupCB)

def ProcessOptions(options, document):
    css = PackageCss(
            renderers='html5',
            path=Path(__file__).parent/'mypkg'/'test.css')
    js = PackageJs(
            renderers='html5',
            path=Path(__file__).parent/'mypkg'/'test.js')
    tpl = PackageTemplateDir(
            renderers='html5',
            path=Path(__file__).parent/'mypkg')

    def cb(document):
        document.userdata['testing'] = 'test'
        return []

    callback = PackagePreCleanupCB(renderers='html5', data=cb)
    document.addPackageResource([css, js, tpl, callback])
