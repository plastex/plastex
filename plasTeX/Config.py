#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# Encodings
#

encoding = c.add_section('encoding')

encoding['input'] = StringOption(
    """ Input encoding """,
    options = '--input-encoding',
    default = 'utf-8',
)

encoding['output'] = StringOption(
    """ Output encoding """,
    options = '--output-encoding',
    default = 'utf-8',
)

#
# Table of Contents
#

toc = c.add_section('tableofcontents')

toc['depth'] = IntegerOption(
    """ Maximum number of levels in each table of contents """,
    options = '--toc-depth',
    default = 2,
)

toc['location'] = MultiOption(
    """ 
    Location to place the table of contents 

    Valid Values: 
    top, bottom

    """,
    options = '--toc-position',
    default = ['top'],
)

#
# Filenames
#

files = c.add_section('filenames')

files['index'] = StringOption(
    """ Name of the first file in the document """,
    options = '--index-file',
    default = 'index',
)

files['template'] = StringOption(
    """ Template to use for non-index filenames """,
    options = '--filename-template',
    default = 'sect%(num).4d',
)

files['extension'] = StringOption(
    """ File extension for output files """,
    options = '--file-extension',
    default = '.html',
)

files['use-ids'] = BooleanOption(
    """ Use IDs (i.e. \\label{...}) as filename """,
    options = '--use-id-filenames',
    default = True,
)

#
# Images
#

images = c.add_section('images')

images['enabled'] = BooleanOption(
    """ Enable/disable image generation """,
    options = '--enable-images !--disable-images',
    default = True,
)

images['image-format'] = StringOption(
    """ PIL image format name """,
    options = '--image-format',
    default = 'PNG',
)

images['file-template'] = StringOption(
    """ Template for image filenames """,
    options = '--image-file-template',
    default = 'img-%03d',
)

images['file-extension'] = StringOption(
    """ Image file extension """,
    options = '--image-file-extension',
    default = '.png',
)

images['image-path'] = StringOption(
    """ Path where images should be generated """,
    options = '--image-path',
    default = 'images',
)

images['latex-file'] = StringOption(
    """ Image document filename """,
    default = 'plastex-images.tex',
)

images['baseline-padding'] = IntegerOption(
    """ Amount to pad the image below the baseline """,
    options = '--image-baseline-padding',
    default = 0,
)

images['smoothing-factor'] = IntegerOption(
    """ Smoothing for images """,
    options = '--image-smoothing-factor',
    default = 6,
)

images['cleanup'] = BooleanOption(
    """ Should the temporary processing files be cleaned up? """,
    default = 1,
)



config.read('~/.plasTeXrc')
config.read('/usr/local/etc/plasTeXrc')
config.read(os.path.join(os.path.dirname(__file__), 'plasTeXrc'))

del c
