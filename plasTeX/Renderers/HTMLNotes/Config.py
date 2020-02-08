from plasTeX.ConfigManager import *
from plasTeX.DOM import Node

config = ConfigManager()
section = config.add_section('htmlNotes')
config.add_category('htmlNotes', 'HTMLNotes renderer options')

section['display-toc'] = BooleanOption(
    """ Display a table of contents on each page """,
    options='--html-notes-display-toc !--html-notes-no-toc',
    category='htmlNotes',
    default=True,
)

section['localtoc-level'] = IntegerOption(
    """ Create a local table of contents above this level """,
    options='--html-notes-localtoc-level',
    category='htmlNotes',
    default=Node.DOCUMENT_LEVEL-1,
)

section['breadcrumbs-level'] = IntegerOption(
    """ Create breadcrumbs from this level """,
    options='--html-notes-breadcrumbs-level',
    category='htmlNotes',
    default=-10,
)

section['mathjax-url'] = StringOption(
    """ Url of the MathJax lib """,
    options='--html-notes-mathjax-url',
    category='htmlNotes',
    default='https://cdn.jsdelivr.net/npm/mathjax@3/es5/'
            'tex-chtml-full.js',
)
