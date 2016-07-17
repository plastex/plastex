import os
import tempfile
from jinja2 import Template
from bs4 import BeautifulSoup

from plasTeX import Environment, Command

class tikzcd(Environment):
    """
    A tikcz-cd diagram whose content will be converted in the processFileContent callback.
    """

class ar(Command):
    pass

class rar(Command):
    pass

class lar(Command):
    pass

class drar(Command):
    pass

class dlar(Command):
    pass

class ular(Command):
    pass

class urar(Command):
    pass

def tikzConvert(document, content):
    tmp_dir = document.userdata['tikzcd']['tmp_dir']
    working_dir = document.userdata['working-dir']
    target_dir = os.path.join(working_dir, document.config['files']['directory'], 'images')
    template = document.userdata['tikzcd']['template']

    cwd = os.getcwd()
    os.chdir(tmp_dir)
    soup = BeautifulSoup(content, "html.parser")
    encoding = soup.original_encoding

    tikzcds = soup.findAll('tikzcd')
    for tikzcd in tikzcds:
        cd_id = tikzcd.attrs['id']
        basepath = os.path.join(tmp_dir, cd_id)
        texpath = basepath + '.tex'
        pdfpath = basepath + '.pdf'
        svgpath =  basepath + '.svg'

        context = {'diagram': tikzcd.text.strip() }
        template.stream(**context).dump(texpath, encoding)

        os.system('xelatex ' + texpath)
        os.system('pdf2svg '+ pdfpath + ' ' + svgpath)
        os.system('mv ' + svgpath + ' ' + target_dir)

        obj = soup.new_tag(
                'object', 
                type='image/svg+xml',
                data='images/' + cd_id + '.svg')
        obj.string = document.context.terms.get(
                'Commutative diagram',
                'Commutative diagram')
        obj.attrs['class'] = 'tikzcd' 
        tikzcd.replace_with(obj)
    os.chdir(cwd)
    return unicode(soup)

def ProcessOptions(options, document):
    """This is called when the package is loaded."""
    
    if 'template' in options:
        with open(options['template'], "r") as file:
            template = file.read()
    else:
        template = u"\\documentclass{standalone}\n\\usepackage{tikz-cd}" + \
                   u"\\begin{document}{{ diagram }}\\end{document}"
    document.userdata['tikzcd'] = {
            'template': Template(template),
            'tmp_dir': tempfile.mkdtemp()}
    processFileContents = document.userdata.get('processFileContents', [])
    processFileContents.append(tikzConvert)
    document.userdata['processFileContents'] = processFileContents

