from plasTeX.ConfigManager import *
from plasTeX.DOM import Node


config = ConfigManager()

section = config.add_section('html5')

config.add_category('html5', 'Html5 renderer Options')

section['extra-css'] = MultiOption(
    """ Extra css files to use """,
    options='--extra-css',
    category='html5',
    default='',
)

section['extra-js'] = MultiOption(
    """ Extra javascript files to use """,
    options='--extra-js',
    category='html5',
    default='',
)

section['theme-css'] = StringOption(
    """ Theme css file""",
    options='--theme-css',
    category='html5',
    default='green',
)

section['use-theme-css'] = BooleanOption(
    """ Use theme css """,
    options='--use-theme-css !--no-theme-css',
    category='html5',
    default=True,
)

section['use-theme-js'] = BooleanOption(
    """ Use theme javascript """,
    options='--use-theme-js !--no-theme-js',
    category='html5',
    default=True,
)

section['display-toc'] = BooleanOption(
    """ Display table of contents on each page """,
    options='--display-toc !--no-display-toc',
    category='html5',
    default=True,
)

section['localtoc-level'] = IntegerOption(
    """ Create local toc above this level """,
    options='--localtoc-level',
    category='html5',
    default=Node.DOCUMENT_LEVEL-1,
)

section['breadcrumbs-level'] = IntegerOption(
    """ Create breadcrumbs from this level """,
    options='--breadcrumbs-level',
    category='html5',
    default=-10,
)

section['use-mathjax'] = BooleanOption(
    """ Use mathjax """,
    options='--use-mathjax !--no-mathjax',
    category='html5',
    default=True,
)

section['mathjax-url'] = StringOption(
    """ Url of the MathJax lib """,
    options='--mathjax-url',
    category='html5',
    default='http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML',
)

section['mathjax-dollars'] = BooleanOption(
    """ Use single dollars as math delimiter for mathjax """,
    options='--dollars !--no-dollars',
    category='html5',
    default=False,
)

section['filters'] = MultiOption(
    """Comma separated list of commands to invoke on each output page.""",
    options='--filters',
    category='html5',
    default='',
)

section['tikz-compiler'] = StringOption(
    """ LaTeX compiler for TikZ pictures """,
    options='--tikz-compiler',
    category='html5',
    default='pdflatex',
)

section['tikz-converter'] = StringOption(
    """ PDF to SVG converter for tikz and tikz-cd """,
    options='--tikz-converter',
    category='html5',
    default='pdf2svg',
)

section['tikz-template'] = StringOption(
    """ Jinja2 template file for tikz """,
    options='--tikz-template',
    category='html5',
    default='',
)

section['tikz-cd-template'] = StringOption(
    """ Jinja2 template file for tikz-cd """,
    options='--tikz-cd-template',
    category='html5',
    default='',
)
