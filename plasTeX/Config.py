#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# Images
#

images = c.add_section('images')

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
    default = 10,
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
