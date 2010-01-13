#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# General
#
general = c.add_section('general')

general['renderer'] = StringOption(
    """ Renderer to use for conversion """,
    options = '--renderer',
    default = 'XHTML',
)

general['theme'] = StringOption(
    """ Theme for the renderer to use """,
    options = '--theme',
    default = 'default',
)

general['copy-theme-extras'] = BooleanOption(
    """  Copy files associated with the theme to the output directory """,
    options = '--copy-theme-extras !--no-theme-extras',
    default = True,
)

general['kpsewhich'] = StringOption(
    """ Program which locates LaTeX files and packages """,
    options = '--kpsewhich',
    default = 'kpsewhich',
)

general['xml'] = BooleanOption(
    """ Dump XML representation of the document (for debugging) """,
    options = '--xml',
    default = False,
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
    callback = readconfig,
)

general['paux-dirs'] = MultiOption(
    """
    Directories where *.paux files should be loaded from.

    """,
    options = '--paux-dirs',
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

links[';links'] = CompoundOption(
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

counters[';counters'] = CompoundOption(
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

files['escape-high-chars'] = BooleanOption(
    """ Escape characters that are higher than 7-bit """,
    options = '--escape-high-chars',
    default = False,
    category = 'files',
)

files['split-level'] = IntegerOption(
    """ Highest section level that generates a new file """,
    options = '--split-level',
    default = 2,
    category = 'files',
)

def setFilename(data):
    """ If there is only one filename specified, turn off splitting """
    data = data.strip()
    if ' ' in data:
        return data
    if '[' in data:
        return data
    files['split-level'] = -10
    return data

files['filename'] = StringOption(
    """ Template for output filenames """,
    options = '--filename',
    default = 'index [$id, sect$num(4)]',
    category = 'files',
    callback = setFilename,
)

files['bad-chars'] = StringOption(
    """ Characters that should not be allowed in a filename """,
    options = '--bad-filename-chars',
    default = ': #$%^&*!~`"\'=?/{}[]()|<>;\\,.',
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

images['base-url'] = StringOption(
    """ Base URL for all images """,
    options = '--image-base-url',
    category = 'images',
)

images['enabled'] = BooleanOption(
    """ Enable image generation """,
    options = '--enable-images !--disable-images',
    default = True,
    category = 'images',
)

images['imager'] = StringOption(
    """ LaTeX to image program """,
    options = '--imager',
    default = 'dvipng dvi2bitmap pdftoppm gspdfpng gsdvipng OSXCoreGraphics',
    category = 'images',
)

images['vector-imager'] = StringOption(
    """ LaTeX to vector image program """,
    options = '--vector-imager',
    default = 'none dvisvgm',
    category = 'images',
)

images['filenames'] = StringOption(
    """ Template for image filenames """,
    options = '--image-filenames',
    default = 'images/img-$num(4)',
    category = 'images',
)

images['baseline-padding'] = IntegerOption(
    """ Amount to pad the image below the baseline """,
    options = '--image-baseline-padding',
    default = 0,
    category = 'images',
)

images['scale-factor'] = FloatOption(
    """ Factor to scale externally included images by """,
    options = '--image-scale-factor',
    default = 1.0,
    category = 'images',
)

images['compiler'] = StringOption(
    """ LaTeX command to use when compiling image document """,
    options = '--image-compiler',
    category = 'images',
)

images['cache'] = BooleanOption(
    """  Enable image caching between runs """,
    options = '--enable-image-cache !--disable-image-cache',
    default = False,
    category = 'images',
)

images['save-file'] = BooleanOption(
    """ Should the temporary images.tex file be saved for debugging? """,
    options = '--save-image-file !--delete-image-file',
    default = False,
    category = 'images',
)

images['transparent'] = BooleanOption(
    """ Specifies whether the image backgrounds should be transparent or not """,
    options = '--transparent-images !--opaque-images',
    default = False,
    category = 'images',
)

images['resolution'] = IntegerOption(
    """ Resolution of images document """,
    options = '--image-resolution',
    default = 0,
    category = 'images',
)

#
# Document
#

doc = c.add_section('document')
c.add_category('document', 'Document Options')

doc['base-url'] = StringOption(
    """ Base URL for inter-node links """,
    options = '--base-url',
    category = 'document',
)

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
    default = 2,
)

doc['index-columns'] = IntegerOption(
    """ Number of columns to split the index entries into """,
    options = '--index-columns',
    category = 'document',
    default = 2,
)

doc['lang-terms'] = StringOption(
    """ Specifies a '%s' delimited list of files that contain language terms """ % os.pathsep,
    options = '--lang-terms',
    category = 'document',
    default = '',
)

config.read('~/.plasTeXrc')
config.read('/usr/local/etc/plasTeXrc')
config.read(os.path.join(os.path.dirname(__file__), 'plasTeXrc'))

del c
