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

section['mathjax-js'] = StringOption(
    """ Url of the MathJax lib """,
    options='--mathjax-js',
    category='html5',
    default='http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML',
)

section['mathjax'] = BooleanOption(
    """ Use mathjax """,
    options='--mathjax !--no-mathjax',
    category='html5',
    default=True,
)

section['font-awesome'] = StringOption(
    """ Url of the Font Awesome lib """,
    options='--font-awesome',
    category='html5',
    default='styles/font-awesome.min.css',
)

