#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX.Tokenizer import Node, Other
from plasTeX import Macro, Command, Environment
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')

class begin(Macro):
    """ Beginning of an environment """

    def invoke(self, tex):
        """ Parse the \\begin{...} """
        name = tex.getArgument(type='str')
        envlog.debug(name)
        obj = tex.context[name]
        obj.macroMode = Macro.MODE_BEGIN
        out = obj.invoke(tex)
        if out is None:
            out = [obj]
        return out

class end(Macro):
    """ End of an environment """

    def invoke(self, tex):
        """ Parse the \\end{...} """
        name = tex.getArgument(type='str')
        envlog.debug(name)
        obj = tex.context[name]
        obj.macroMode = Macro.MODE_END
        out = obj.invoke(tex)
        if out is None:
            out = [obj]
        return out

class newcommand(Command):
    """ \\newcommand """
    args = 'name:cs [ nargs:int ] [ opt:nox ] definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        args = (a['name'], a['nargs'], a['definition'])
        kwargs = {'opt':a['opt']}
        deflog.debug('command %s %s %s', *args)
        tex.context.newcommand(*args, **kwargs)

class renewcommand(newcommand): pass
class providecommand(newcommand): pass

class newenvironment(Command):
    """ \\newenvironment """
    args = 'name:str [ nargs:int ] [ opt:nox ] begin:nox end:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        args = (a['name'], a['nargs'], [a['begin'], a['end']])
        kwargs = {'opt':a['opt']}
        deflog.debug('environment %s %s %s', *args)
        tex.context.newenvironment(*args, **kwargs)

class usepackage(Command):
    """ \\usepackage """
    args = '[ %options ] name:str'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        try: 
            # See if it has already been loaded
            if tex.context.packages.has_key(attrs['name']):
                return

            try: 
                m = __import__(attrs['name'], globals(), locals())
                status.info(' ( %s ' % m.__file__)
                tex.context.importMacros(vars(m))
                tex.context.packages[attrs['name']] = attrs['options']
                status.info(' ) ')
                return

            except ImportError:
                log.warning('No Python version of %s was found' % attrs['name'])

            #path = kpsewhich(attrs['name'])
            path = attrs['name']

            status.info(' ( %s.sty ' % attrs['name'])
            tex.input(open(path, 'r'))
            tex.context.packages[attrs['name']] = attrs['options']
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nError opening package "%s"' % attrs['name'])
            status.info(' ) ')

class documentclass(usepackage):
    """ \\documentclass """

class RequirePackage(usepackage):
    """ \\RequirePackage """

class x_ifnextchar(Command):
    macroName = '@ifnextchar'
    args = 'char:Tok true:nox false:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        for t in tex.itertokens():
            tex.pushtoken(t)
            if a['char'] == t:
                return a['true']
            else:
                return a['false']


class document(Environment):
    level = Node.DOCUMENT_LEVEL
    def toXML(self):
        return '<?xml version="1.0"?>\n%s' % Environment.toXML(self)

class StartSection(Command):
    args = '* [ toc ] title'

    def digest(self, tokens):
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.level <= self.level:
                tokens.push(item)
                break
            if item.nodeType == Node.ELEMENT_NODE:
                item.digest(tokens)
            self.appendChild(item)
    
class chapter(StartSection):
    level = Node.CHAPTER_LEVEL
    counter = 'chapter'

class section(StartSection):
    level = Node.SECTION_LEVEL
    counter = 'section'

class subsection(StartSection):
    level = Node.SUBSECTION_LEVEL
    counter = 'subsection'

class subsubsection(StartSection):
    level = Node.SUBSUBSECTION_LEVEL
    counter = 'subsubsection'

class paragraph(StartSection):
    level = Node.PARAGRAPH_LEVEL
    counter = 'paragraph'

class subparagraph(StartSection):
    level = Node.SUBPARAGRAPH_LEVEL
    counter = 'subparagraph'

class subsubparagraph(StartSection):
    level = Node.SUBSUBPARAGRAPH_LEVEL
    counter = 'subsubparagraph'

class vspace(Command):
    args = '* length:str'

class hspace(Command):
    args = '* length:str'

class pagebreak(Command): 
    pass

class label(Command):
    args = 'label:id'


class setcounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.counters[a['name']] = a['value']

class addtocounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.counters[a['name']] += a['value']

class stepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        tex.context.counters[a['name']] += 1

class refstepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        tex.context.counters[self.parse(tex)['name']] += 1

class arabic(Command):
    """ Return arabic representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other(tex.context.counters[self.parse(tex)['name']])]

class Roman(Command):
    """ Return uppercase roman representation """
    args = 'name:str'
    def invoke(self, tex):
        roman = ""
        n, number = divmod(tex.context.counters[self.parse(tex)['name']], 1000)
        roman = "M"*n
        if number >= 900:
            roman = roman + "CM"
            number = number - 900
        while number >= 500:
            roman = roman + "D"
            number = number - 500
        if number >= 400:
            roman = roman + "CD"
            number = number - 400
        while number >= 100:
            roman = roman + "C"
            number = number - 100
        if number >= 90:
            roman = roman + "XC"
            number = number - 90
        while number >= 50:
            roman = roman + "L"
            number = number - 50
        if number >= 40:
            roman = roman + "XL"
            number = number - 40
        while number >= 10:
            roman = roman + "X"
            number = number - 10
        if number >= 9:
            roman = roman + "IX"
            number = number - 9
        while number >= 5:
            roman = roman + "V"
            number = number - 5
        if number >= 4:
            roman = roman + "IV"
            number = number - 4
        while number > 0:
            roman = roman + "I"
            number = number - 1
        return [Other(roman)]

class roman(Roman):
    """ Return the lowercase roman representation """
    def invoke(self, tex):
        return [Other(x.lower()) for x in Roman.invoke()]

class Alph(Command):
    """ Return the uppercase letter representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other(tex.context.counters[self.parse(tex)['name']]-1).upper()]

class alph(Alph):
    """ Return the lowercase letter representation """
    def invoke(self, tex):
        return [Other(x.lower()) for x in Alph.invoke()]

class fnsymbol(Command):
    """ Return the symbol representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other('*' * self.value)]
