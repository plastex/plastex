import os
import tempfile
from jinja2 import Template
from bs4 import BeautifulSoup

from plasTeX import Environment, Command

from plasTeX.Packages import tikz

class tikzcd(Environment):
    """
    A tikz-cd diagram whose content will be converted in the processFileContent callback.
    """

class ar(Command):
    pass

class rar(Command):
    pass

class lar(Command):
    pass

class uar(Command):
    pass

class drar(Command):
    pass

class dar(Command):
    pass

class dlar(Command):
    pass

class ular(Command):
    pass

class urar(Command):
    pass


def ProcessOptions(options, document):
    """This is called when the package is loaded."""
    
    if 'template' in options:
        with open(options['template'], "r") as file:
            template = file.read()
    else:
        template = u"\\documentclass{standalone}\n\\usepackage{tikz-cd}" + \
                   u"\\begin{document}{{ tikzpicture }}\\end{document}"
    document.userdata['tikzcd'] = {
            'template': Template(template),
            'tmp_dir': tempfile.mkdtemp()}

    def convert(document, content):
        return tikz.tikzConvert(
                document, 
                content, 
                'tikzcd', 
                'Commutative diagram')

    document.userdata.setdefault('processFileContents', []).append(convert)
