#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# Encodings
#

encoding = c.add_section('encoding')
c.add_category('encoding', 'Encoding Options')

encoding['input'] = StringOption(
    """ Input encoding """,
    options = '--input-encoding',
    default = 'utf-8',
    category = 'encoding',
)

encoding['output'] = StringOption(
    """ Output encoding """,
    options = '--output-encoding',
    default = 'utf-8',
    category = 'encoding',
)

#
# Files
#

files = c.add_section('files')
c.add_category('files', 'File Handling Options')

files['split-level'] = IntegerOption(
    """ Level to split the document into files """,
    options = '--split-level',
    default = 2,
    category = 'files',
)

files['index'] = StringOption(
    """ Name of the first file in the document """,
    options = '--index-file',
    default = 'index',
    category = 'files',
)

files['template'] = StringOption(
    """ Template to use for non-index filenames """,
    options = '--filename-template',
    default = 'sect%(num).4d',
    category = 'files',
)

files['extension'] = StringOption(
    """ File extension for output files """,
    options = '--file-extension',
    default = '.html',
    category = 'files',
)

files['use-ids'] = BooleanOption(
    """ Use IDs (i.e. \\label{...}) as filename """,
    options = '--use-id-filenames',
    default = True,
    category = 'files',
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



config.read('~/.plasTeXrc')
config.read('/usr/local/etc/plasTeXrc')
config.read(os.path.join(os.path.dirname(__file__), 'plasTeXrc'))

del c
