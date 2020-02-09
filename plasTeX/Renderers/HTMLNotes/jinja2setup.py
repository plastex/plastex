# Jinja2 setup for the HTMLNotes renderer

import datetime

from plasTeX.Logging import getLogger
from plasTeX.Renderers import PageTemplate


log = getLogger()

try:
    import jinja2
except ImportError:
    log.error('Jinja2 unavailable,'
              ' HTMLNotes renderer cannot be used')


try:
    from jinja2_ansible_filters import AnsibleCoreFiltersExtension
except ImportError:
    AnsibleCoreFiltersExtension = None

if not AnsibleCoreFiltersExtension:
    log.error('Jinja2-ansible-filters unavailable,'
              ' HTMLNotes renderer cannot be used')


PageTemplate.jinja2_extensions.add(AnsibleCoreFiltersExtension)


def format_datetime(thing, input_format, output_format):
    datetime_object = datetime.datetime.strptime(str(thing),
                                                 input_format)
    return datetime.datetime.strftime(datetime_object, output_format)


PageTemplate.jinja2_filters['format_datetime'] = format_datetime


def escape_html(string):
    return (string
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


PageTemplate.jinja2_filters['escape_html'] = escape_html

# End of file
