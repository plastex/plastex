#!/usr/bin/env python

"""
C.8 Definitions, Numbering, and Programming

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')

#
# C.8.1 Defining Commands
#

class newcommand(Command):
    """ \\newcommand """
    args = '* name:cs [ nargs:int ] [ opt:nox ] definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        args = (a['name'], a['nargs'], a['definition'])
        kwargs = {'opt':a['opt']}
        deflog.debug('command %s %s %s', *args)
        self.ownerDocument.context.newcommand(*args, **kwargs)

class renewcommand(newcommand): 
    pass

class providecommand(newcommand): 
    pass

class DeclareRobustCommand(newcommand):
    pass

class DeclareTextCommandDefault(newcommand):
    pass

#
# C.8.2 Defining Environments
#

class newenvironment(Command):
    """ \\newenvironment """
    args = '* name:str [ nargs:int ] [ opt:nox ] begin:nox end:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        args = (a['name'], a['nargs'], [a['begin'], a['end']])
        kwargs = {'opt':a['opt']}
        deflog.debug('environment %s %s %s', *args)
        self.ownerDocument.context.newenvironment(*args, **kwargs)

class renewenvironment(newenvironment):
    pass


#
# C.8.3 Theorem-like Environments
#

class newtheorem(Command):
    args = 'name:str [ counter:str ] caption [ within:str ]'
