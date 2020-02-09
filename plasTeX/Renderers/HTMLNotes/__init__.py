# plasTeX HTMLNotes renderer

import glob
import os
import re

from plasTeX.Logging import getLogger
from plasTeX.Renderers import PageTemplate
from plasTeX.Renderers.HTMLNotes import filenameoverride, jinja2setup


def set_up_css_js(document):
    renderer_data = document.rendererdata['htmlNotes'] = {}
    config = document.config
    renderer_data['css'] = [
        'theme-' + config['general']['theme'] + '.css'
    ]
    renderer_data['js'] = [
        'jquery.min.js',
        'plastex.js',
        'svgxuse.js',
    ]


class HTMLNotes(PageTemplate.Renderer):
    fileExtension = '.html'
    imageTypes = ['.svg', '.png', '.jpg', '.jpeg', '.gif']
    vectorImageTypes = ['.svg']

    def load_template_directory(self):
        this_directory = os.path.dirname(__file__)
        template_directory = os.path.join(this_directory,
                                          'Templates')
        directories = glob.glob('%s%s**%s' % (template_directory,
                                              os.sep,
                                              os.sep),
                                recursive=True)
        log = getLogger()
        log.info('Importing templates recursively from %s'
                 % template_directory)
        for directory in directories:
            super().importDirectory(directory)

    def load_all_templates(self, document):
        self.load_template_directory()
        super().loadTemplates(document)

    def set_up_package_resources(self, document):
        build_directory = os.getcwd()
        for resource in document.packageResources:
            resource.alter(renderer=self, rendererName='htmlNotes',
                           document=document, target=build_directory)

    def loadTemplates(self, document):
        self.load_all_templates(document)
        set_up_css_js(document)
        self.set_up_package_resources(document)

    def processFileContent(self, document, string):
        string = super().processFileContent(document, string)
        string = re.compile(r'<p>\s*</p>', re.I).sub(r'', string)
        string = (re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I)
                  .sub(r'\1&nbsp;\3', string))
        return string


Renderer = HTMLNotes

# End of file
