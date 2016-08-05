import os
from plasTeX.ConfigManager import *

config = ConfigManager()

section = config.add_section('html5')

config.add_category('html5', 'Html5 renderer Options')

section['extra-css'] = StringOption(
    """ Extra css file to use """,
    options='--extra-css',
    category='html5',
    default='',
)

section['theme-css'] = BooleanOption(
    """ Use theme css file""",
    options='--theme-css',
    category='html5',
    default=True,
)

section['mathjax-js'] = StringOption(
    """ Url of the MathJax lib """,
    options='--mathjax-js',
    category='html5',
    default='http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_CHTML',
)

section['mathjax'] = BooleanOption(
    """ Use mathjax """,
    options='--mathjax !--no-mathjax',
    category='html5',
    default=True,
)

section['filters'] = MultiOption(
    """Comma separated list of commands to invoke on each output page.""",
    options='--filters',
    category='html5',
    default='',
)
