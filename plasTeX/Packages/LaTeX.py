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
