#!/usr/bin/env python

from plasTeX.Token import *
from plasTeX import Macro, Command, Environment
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')

class begin(Macro):
    """ Beginning of an environment """

    def invoke(self, tex):
        """ Parse the \\begin{...} """
        name = tex.getArgument(type='str')
        envlog.debug(name)
        tex.context.push()
        obj = tex.context[name]
        obj.mode = MODE_BEGIN
        return obj.invoke(tex)

class end(Macro):
    """ End of an environment """

    def invoke(self, tex):
        """ Parse the \\end{...} """
        name = tex.getArgument(type='str')
        envlog.debug(name)
        obj = tex.context[name]
        obj.mode = MODE_END
        output = obj.invoke(tex)
        tex.context.pop()
        return output

class newcommand(Command):
    """ \\newcommand """
    args = 'name:cs [ nargs:int ] [ opt:nox ] definition:nox'
    def invoke(self, tex):
        Command.parse(self, tex)
        a = self.attributes
        args = (a['name'], a['nargs'], a['definition'])
        kwargs = {'opt':a['opt']}
        deflog.debug('command %s %s %s', *args)
        print args
        tex.context.newcommand(*args, **kwargs)
        return [self]

class renewcommand(newcommand): pass
class providecommand(newcommand): pass

class newenvironment(Command):
    """ \\newenvironment """
    args = 'name:str [ nargs:int ] [ opt ] begin end'
    def invoke(self, tex):
        Command.parse(self, tex)
        a = self.attributes
        args = (a['name'], a['nargs'], [a['begin'], a['end']])
        kwargs = {'opt':a['opt']}
        deflog.debug('environment %s %s %s', *args)
        tex.context.newenvironment(*args, **kwargs)
        return [self]

class usepackage(Command):
    """ \\usepackage """
    args = '[ %options ] $name'
    loaded = {}
    def invoke(self, tex):
        attrs = self.attributes
        Command.parse(self, tex)
        try: 
            # See if it has already been loaded
            if type(self).loaded.has_key(attrs['name']):
                return

            try: 
                m = __import__(attrs['name'], globals(), locals())
                status.info(' ( %s ' % m.__file__)
                tex.context.importMacros(vars(m))
                type(self).loaded[attrs['name']] = attrs['options']
                status.info(' ) ')
                return

            except ImportError:
                log.warning('No Python version of %s was found' % attrs['name'])

            path = kpsewhich(attrs['name'])

            status.info(' ( %s.sty ' % attrs['name'])
            type(tex)(open(path)).parse()
            type(self).loaded[self.name] = attrs['options']
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nError opening package "%s"' % attrs['name'])
            status.info(' ) ')

        return [self]

class documentclass(usepackage):
    """ \\documentclass """
    def invoke(self, tex):
        usepackage.parse(self, tex)
        from plasTeX import packages
        tex.context.importMacros(vars(packages))
        return [self]

class RequirePackage(usepackage):
    """ \\RequirePackage """

class x_ifnextchar(Command):
    texname = '@ifnextchar'
    def invoke(self, tex):
        char = tex.getArgument()[0]
        truecontent = tex.getArgument()
        falsecontent = tex.getArgument()
        for t in tex.itertokens():
            tex.pushtoken(t)
            if char == t:
                return truecontent
            else:
                return falsecontent
