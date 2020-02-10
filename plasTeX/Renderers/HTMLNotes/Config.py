# Options for the HTMLNotes renderer

from plasTeX.ConfigManager import *
from plasTeX.DOM import Node

config = ConfigManager()
section = config.add_section('htmlNotes')
config.add_category('htmlNotes', 'HTMLNotes renderer options')

section['display-toc'] = BooleanOption(
    """ Display a table of contents on each page """,
    category='htmlNotes',
    default=True,
    options='--html-notes-display-toc !--html-notes-no-toc',
)

section['localtoc-level'] = IntegerOption(
    """ Create a local table of contents above this level """,
    category='htmlNotes',
    default=Node.DOCUMENT_LEVEL-1,
    options='--html-notes-localtoc-level',
)

section['breadcrumbs-level'] = IntegerOption(
    """ Create breadcrumbs from this level """,
    category='htmlNotes',
    default=-10,
    options='--html-notes-breadcrumbs-level',
)

section['mathjax-url'] = StringOption(
    """ URL of the MathJax script """,
    category='htmlNotes',
    default='https://cdn.jsdelivr.net/npm/mathjax@3/es5/'
            'tex-chtml-full.js',
    options='--html-notes-mathjax-url',
)

# End of file
