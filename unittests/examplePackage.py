from plasTeX.PackageResource import (
	PackageResource, PackageCss, PackageJs, PackageTemplateDir)
from plasTeX import Command

def ProcessOptions(options, document):
	css = PackageCss(
		renderers='html5',
		data='test.css',
		package='mypkg')
	js = PackageJs(
		renderers='html5',
		data='test.js',
		package='mypkg')
	tpl = PackageTemplateDir(
		renderers='html5',
		package='mypkg')

	def cb(document):
		document.userdata['testing'] = 'test'
		return []

	callback = PackageResource(
		renderers='html5',
		key='preCleanupCallbacks',
		data=cb)
	document.addPackageResource([css, js, tpl, callback])