#!/usr/bin/env python

import os
from ConfigManager import *

c = config = ConfigManager()

#
# Renderer
#
general = c.add_section('general')
c.add_category('general', 'General Options')

general['renderer'] = StringOption(
    """ Renderer to use for conversion """,
    options = '--renderer',
    default = 'xhtml',
    category = 'general',
)

#
# Files
#

files = c.add_section('files')
c.add_category('files', 'File Handling Options')

files['input'] = StringOption(
    """ Input file encoding """,
    options = '--input-encoding',
    default = 'utf-8',
    category = 'files',
)

files['output'] = StringOption(
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

files['index'] = StringOption(
    """ Basename of the first output file """,
    options = '--index-file',
    default = 'index',
    category = 'files',
)

files['basename'] = StringOption(
    """ Template to use for the basename of output files """,
    options = '--file-basename',
    default = 'sect%(num).4d',
    category = 'files',
)

files['filename'] = StringOption(
    """ Template for output filenames """,
    options = '--filename',
    default = '%(basename)s.html',
    category = 'files',
)

files['use-ids'] = BooleanOption(
    """ Use IDs (i.e. \\label{...}) as filename """,
    options = '--filenames-use-id',
    default = True,
    category = 'files',
)

files['bad-chars'] = StringOption(
    """ Characters that should not be allowed in a filename """,
    options = '--bad-filename-chars',
    default = ':#$%^&*!~`"\'=?/{}[]()|<>;\\,',
    category = 'files',
)

files['bad-chars-sub'] = StringOption(
    """ Character that should be used instead of an illegal character """,
    options = '--bad-filename-chars-sub',
    default = '_',
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

#
# Document
#

doc = c.add_section('doc')
c.add_category('doc', 'Document Options')

doc['title'] = StringOption(
    """ 
    Title for the document 

    This option specifies a title to use instead of the title
    specified in the LaTeX document.

    """,
    options = '--title',
    category = 'doc',
)


config.read('~/.plasTeXrc')
config.read('/usr/local/etc/plasTeXrc')
config.read(os.path.join(os.path.dirname(__file__), 'plasTeXrc'))

del c
