#!/usr/bin/env python

from plasTeX import Macro, Command, Environment, MODE_BEGIN, MODE_END
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
        obj.mode = MODE_BEGIN
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
        obj.mode = MODE_END
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
    texname = '@ifnextchar'
    args = 'char:tok true:nox false:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        for t in tex.itertokens():
            tex.pushtoken(t)
            if a['char'] == t:
                return a['true']
            else:
                return a['false']


class chaphead(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headi(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headii(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headiii(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headiv(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headv(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class headvi(Command):
    args = '[ toc ] ( helptag:str ) label:str title'
class syni(Command):
    args = 'entry'
class sbji(Command):
    args = 'entry'
class ssbji(Command):
    args = 'entry subentry'
class ssyni(Command):
    args = 'entry subentry'
class sbjsee(Command):
    args = 'entry see'
class datastep(Command):
    args = 'file:str'
class sascode(Command):
    args = 'file:str'
class sasout(Command):
    args = 'width:str file:str [ %options ]'
class sasop(Command):
    args = '( helptag:str ) label:str title'
class sasstmt(Command):
    args = '* statement options'
class help(Command):
    args = 'text'
class xhelp(Command):
    args = 'text'
class ssbifourteen(Environment):
    pass
class hv(Environment):
    pass
class fref(Command):
    args = '[ type:str ] label:str'
class quotes(Command):
    args = 'text'
class ssbeleven(Environment):
    pass
class ssiten(Environment):
    pass
class colon(Command):
    pass
class sref(Command):
    args = '[ type:str ] label:str'
class chapref(Command):
    args = '[ type:str ] label:str'
class oref(Command):
    args = '[ type:str ] label:str'
class tablehead(Command):
    args = 'label:str title'
class examplehead(Command):
    args = 'label:str title'
class textpercent(Command):
    texname = '%'
class alpha(Command): pass
class textdollar(Command):
    texname = '$'
class sigma(Command): pass
class prime(Command): pass
class htmlref(Command):
    args = 'text label:str'
class fsbji(Command):
    args = 'key entry'
class setlength(Command):
    args = 'length:cs value:str'
class textunderscore(Command):
    texname = '_'
class fssbji(Command):
    args = 'key entry1 entry2'
class frac(Command):
    args = 'numerator denominator'
class bar(Command):
    args = 'text'
class displaystyle(Command): pass
class sqrt(Command):
    args = 'text'
class max(Command): pass
class min(Command): pass
class quad(Command): pass
class ne(Command): pass
class left(Command):
    args = 'char'
class right(Command):
    args = 'char'
class pm(Command): pass
class mu(Command): pass
class lbrace(Command): pass
class _lbrace(Command): 
    texname = '{'
class rbrace(Command): pass
class _rbrace(Command): 
    texname = '}'
class chi(Command): pass
class leq(Command): pass
class int(Command): pass
class geq(Command): pass
class dashtwo(Command): pass
class textampersand(Command):
    texname = '&'

class sasstmts(Environment):
    class item(Command): pass
class reference(Environment):
    class item(Command): pass

#class begindisplaymath(Definition):
#    definition = r'\begin{displaymath}'
#class enddisplaymath(Definition):
#    definition = r'\end{displaymath}'
