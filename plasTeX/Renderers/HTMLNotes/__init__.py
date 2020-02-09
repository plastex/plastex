# plasTeX HTMLNotes renderer

import datetime
import glob
import os
import re
import sys

from plasTeX import Base, Command
from plasTeX.Logging import getLogger
from plasTeX.Renderers.PageTemplate import Renderer as \
    PageTemplateRenderer

log = getLogger()
this_directory = os.path.dirname(__file__)


def add_package_directory():
    import plasTeX
    plastex_directory = os.path.dirname(plasTeX.__file__)
    del plasTeX
    package_directory = os.path.join(plastex_directory,
                                     'LocalPackages')
    sys.path.append(package_directory)


add_package_directory()

try:
    import jinja2
except ImportError:
    jinja2 = None

if not jinja2:
    log.error('Jinja2 unavailable,'
              ' HTMLNotes renderer cannot be used')

try:
    from jinja2_ansible_filters import AnsibleCoreFiltersExtension
except ImportError:
    AnsibleCoreFiltersExtension = None

if not AnsibleCoreFiltersExtension:
    log.error('Jinja2-ansible-filters unavailable,'
              ' HTMLNotes renderer cannot be used')


class SetTitle(Command):
    args = 'self'

    def invoke(self, tex):
        super().invoke(tex)
        self.ownerDocument.userdata['SetTitle'] = self


Base.SetTitle = SetTitle


def format_datetime(thing, input_format, output_format):
    datetime_object = datetime.datetime.strptime(str(thing),
                                                 input_format)
    return datetime.datetime.strftime(datetime_object, output_format)


def escape_html(string):
    return (string
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def jinja2_template(string, encoding='utf8'):
    environment = jinja2.Environment(trim_blocks=True,
                                     lstrip_blocks=True)
    environment.add_extension(AnsibleCoreFiltersExtension)
    environment.filters['format_datetime'] = format_datetime
    environment.filters['escape_html'] = escape_html

    def render_jinja2(obj, s=string):
        template_variables = {
            'here': obj,
            'obj': obj,
            'container': obj.parentNode,
            'config': obj.ownerDocument.config,
            'context': obj.ownerDocument.context,
            'templates': obj.renderer
        }
        template = environment.from_string(s)
        return template.render(template_variables)

    return render_jinja2


def file_name_from_label(node):
    label_descendants = node.getElementsByTagName('label')

    if label_descendants:
        label_node = label_descendants[0]
        label_value = label_node.attributes['label']
        if label_value:
            bad_characters = ': #$%^&*!~`"\'=?/{}[]()|<>;\\,.'
            replacement = '-'
            for character in bad_characters:
                label_value = label_value.replace(character,
                                                  replacement)
            return label_value
    else:
        return id(node)

    AttributeError, 'Node %s does not have a label' % node


Base.section.filenameoverride = property(file_name_from_label)


class HTMLNotes(PageTemplateRenderer):
    fileExtension = '.html'
    imageTypes = ['.svg', '.png', '.jpg', '.jpeg', '.gif']
    vectorImageTypes = ['.svg']

    def __init__(self, *arguments, **keyword_arguments):
        super().__init__(self, *arguments, **keyword_arguments)
        super().registerEngine('jinja2', None, '.jinja2',
                               jinja2_template)

    def loadTemplates(self, document):
        template_directory = os.path.join(this_directory,
                                          'Templates')
        directories = glob.glob('%s%s**%s' % (template_directory,
                                              os.sep,
                                              os.sep),
                                recursive=True)

        log.info('Importing templates recursively from %s'
                 % template_directory)

        for directory in directories:
            super().importDirectory(directory)

        super().loadTemplates(document)

        renderer_data = document.rendererdata['htmlNotes'] = dict()
        config = document.config
        build_directory = os.getcwd()

        renderer_data['css'] = [
            'theme-' + config['general']['theme'] + '.css'
        ]

        renderer_data['js'] = [
            'jquery.min.js',
            'plastex.js',
            'svgxuse.js',
        ]

        for resource in document.packageResources:
            resource.alter(renderer=self, rendererName='htmlNotes',
                           document=document, target=build_directory)

    def processFileContent(self, document, string):
        string = super().processFileContent(document, string)
        string = re.compile(r'<p>\s*</p>', re.I) .sub(r'', string)
        string = (re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I)
                  .sub(r'\1&nbsp;\3', string))

        return string


Renderer = HTMLNotes

# End of file
