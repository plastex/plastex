"""
Implement the tikz package for html output.
The original tikz and xelatex do most of the work and then pdf2svg turns it
into a svg image.
Needs Beautiful Soup, Jinja2 and pdf2svg
"""

import os
import tempfile
from jinja2 import Template
from bs4 import BeautifulSoup

from plasTeX import Environment, Command

class tikzpicture(Environment):
    """
    A tikz picture whose content will be converted in the processFileContent callback.
    """
    class draw(Command):
        pass

def tikzConvert(document, content, envname, placeholder):
    tmp_dir = document.userdata[envname]['tmp_dir']
    working_dir = document.userdata['working-dir']
    target_dir = os.path.join(working_dir, document.config['files']['directory'], 'images')
    template = document.userdata[envname]['template']

    cwd = os.getcwd()
    os.chdir(tmp_dir)
    soup = BeautifulSoup(content, "html.parser")
    encoding = soup.original_encoding

    envs = soup.findAll(envname)
    for env in envs:
        cd_id = env.attrs['id']
        basepath = os.path.join(tmp_dir, cd_id)
        texpath = basepath + '.tex'
        pdfpath = basepath + '.pdf'
        svgpath =  basepath + '.svg'

        context = {'tikzpicture': env.text.strip() }
        template.stream(**context).dump(texpath, encoding)

        os.system('xelatex ' + texpath)
        os.system('pdf2svg '+ pdfpath + ' ' + svgpath)
        os.system('mv ' + svgpath + ' ' + target_dir)

        obj = soup.new_tag(
                'object', 
                type='image/svg+xml',
                data='images/' + cd_id + '.svg')
        obj.string = document.context.terms.get(
                placeholder,
                placeholder)
        obj.attrs['class'] = envname
        env.replace_with(obj)
    os.chdir(cwd)
    return unicode(soup)

def ProcessOptions(options, document):
    """This is called when the package is loaded."""
    
    if 'template' in options:
        with open(options['template'], "r") as file:
            template = file.read()
    else:
        template = u"\\documentclass{standalone}\n\\usepackage{tikz}" + \
                   u"\\begin{document}{{ tikzpicture }}\\end{document}"
    document.userdata['tikzpicture'] = {
            'template': Template(template),
            'tmp_dir': tempfile.mkdtemp()}

    def convert(document, content):
        return tikzConvert(document, content, 'tikzpicture', 'TikZ picture')

    document.userdata.setdefault('processFileContents', []).append(convert)
