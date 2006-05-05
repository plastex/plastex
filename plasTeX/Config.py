#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# General
#
general = c.add_section('general')
c.add_category('general', 'General Options')

general['renderer'] = StringOption(
    """ Renderer to use for conversion """,
    options = '--renderer',
    default = 'XHTML',
    category = 'general',
)

def readconfig(file):
    """ Read a configuration file """
    if not os.path.isfile(file):
        print >>sys.stderr, "WARNING: Could not load config file '%s'" % file
        return
    config.read(file)

general['config'] = StringOption(
    """ 
    Load additional configuration file 

    This configuration file will be loaded during the processing of
    command-line options.  However, configuration files cannot override
    command-line options.  So no matter what is in the configuration file,
    if an option is specified on the command-line, it will always win.
    To eliminate any confusion, this should generally be the first
    argument.

    """,
    options = '--config -c',
    category = 'general',
    callback = readconfig,
)

#
# Links
#

links = c.add_section('links')

def getstring(data):
    """ Return a string which may or may not be quoted """
    data = list(data.lstrip())

    if not data:
        return ''

    s = []
    for quote in '\'"':
        if data[0] == quote:
            data.pop(0)
            while data:
                if data[0] == quote:
                    data.pop(0)
                    break
                s.append(data.pop(0))
            return ''.join(s), ''.join(data)

    while data:
        if data[0] != ' ':
            s.append(data.pop(0))
            continue
        break
    return ''.join(s), ''.join(data)
    

def setlinks(data):
    """ Set links in the configuration """
    data = data[1:-1].strip()
    key, data = getstring(data)
    url, data = getstring(data)
    title, data = getstring(data)
    if not title:
        title = url
        url = ''
    if title:
        links['%s-title' % key] = StringOption(default=title)
    if url:
        links['%s-url' % key] = StringOption(default=url)

links['#links'] = CompoundOption(
    """ Set links for use in navigation """,
    options = '--link',
    category = 'document',
    callback = setlinks,
)

#
# Counters
#

counters = c.add_section('counters')

def setcounter(data):
    """ Set counters in the configuration """
    value = [x for x in data[1:-1].split() if x]
    if len(value) == 2:
        counters[value[0]] = IntegerOption(default=int(value[1]))

counters['#counters'] = CompoundOption(
    """ Set initial counter values """,
    options = '--counter',
    category = 'document',
    callback = setcounter,
)

#
# Files
#

files = c.add_section('files')
c.add_category('files', 'File Handling Options')

files['input-encoding'] = StringOption(
    """ Input file encoding """,
    options = '--input-encoding',
    default = 'utf-8',
    category = 'files',
)

files['output-encoding'] = StringOption(
    """ Output file encoding """,
    options = '--output-encoding',
    default = 'utf-8',
    category = 'files',
)

files['split-level'] = IntegerOption(
    """ Highest section level that generates a new file """,
    options = '--split-level',
    default = 2,
    category = 'files',
)

files['filename'] = StringOption(
    """ Template for output filenames """,
    options = '--filename',
    default = 'index.html [$id, sect$num(4)].html',
    category = 'files',
)

files['bad-chars'] = StringOption(
    """ Characters that should not be allowed in a filename """,
    options = '--bad-filename-chars',
    default = ' :#$%^&*!~`"\'=?/{}[]()|<>;\\,.',
    category = 'files',
)

files['bad-chars-sub'] = StringOption(
    """ Character that should be used instead of an illegal character """,
    options = '--bad-filename-chars-sub',
    default = '-',
    category = 'files',
)

files['directory'] = StringOption(
    """ Directory to put output files into """,
    options = '--dir -d',
    category = 'files',
    default = '$jobname',
)

#
# Images
#

images = c.add_section('images')
c.add_category('images', 'Image Generation Options')

images['enabled'] = BooleanOption(
    """ Enable/disable image generation """,
    options = '--enable-images !--disable-images',
    default = True,
    category = 'images',
)

images['program'] = StringOption(
    """ DVI to image program """,
    options = '--image-program',
    default = 'dvipng',
    category = 'images',
)

images['image-format'] = StringOption(
    """ PIL image format name """,
    options = '--image-format',
    default = 'PNG',
    category = 'images',
)

images['file-template'] = StringOption(
    """ Template for image filenames """,
    options = '--image-file-template',
    default = 'img-%03d',
    category = 'images',
)

images['file-extension'] = StringOption(
    """ Image file extension """,
    options = '--image-file-extension',
    default = '.png',
    category = 'images',
)

images['image-path'] = StringOption(
    """ Path where images should be generated """,
    options = '--image-path',
    default = 'images',
    category = 'images',
)

images['latex-file'] = StringOption(
    """ Image document filename """,
    default = 'plastex-images.tex',
    category = 'images',
)

images['baseline-padding'] = IntegerOption(
    """ Amount to pad the image below the baseline """,
    options = '--image-baseline-padding',
    default = 0,
    category = 'images',
)

images['smoothing-factor'] = IntegerOption(
    """ Smoothing for images """,
    options = '--image-smoothing-factor',
    default = 6,
    category = 'images',
)

images['cleanup'] = BooleanOption(
    """ Should the temporary processing files be cleaned up? """,
    default = 1,
    category = 'images',
)

#
# Document
#

doc = c.add_section('document')
c.add_category('document', 'Document Options')

doc['title'] = StringOption(
    """ 
    Title for the document 

    This option specifies a title to use instead of the title
    specified in the LaTeX document.

    """,
    options = '--title',
    category = 'document',
)

doc['toc-depth'] = IntegerOption(
    """ Number of levels to display in the table of contents """,
    options = '--toc-depth',
    category = 'document',
    default = 3,
)

doc['toc-non-files'] = BooleanOption(
    """ Display sections that do not create files in the table of contents """,
    options = '--toc-non-files',
    category = 'document',
    default = False,
)

doc['sec-num-depth'] = IntegerOption(
    """ Maximum section depth to display section numbers """,
    options = '--sec-num-depth',
    category = 'document',
    default = 6,
)

#
# Programs
#

prog = c.add_section('programs')
c.add_category('programs', 'External Programs')

prog['kpsewhich'] = StringOption(
    """ Program which locates LaTeX files and packages """,
    options = '--kpsewhich',
    category = 'programs',
    default = 'kpsewhich',
)


config.read('~/.plasTeXrc')
config.read('/usr/local/etc/plasTeXrc')
config.read(os.path.join(os.path.dirname(__file__), 'plasTeXrc'))

del c
