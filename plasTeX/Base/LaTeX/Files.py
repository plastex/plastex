#!/usr/bin/env python

"""
C.11.1 Files (p206)
C.11.4 Splitting the Input
C.11.6 Terminal Input and Output

"""

import codecs
from plasTeX import Command, Environment
from plasTeX.Config import config
from plasTeX.Logging import getLogger

encoding = config['encoding']['input']
log = getLogger()

class nofiles(Command):
    pass

class input(Command):
    """ \\input """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        try: 
            #path = kpsewhich(attrs['name'])
            path = a['name']

            status.info(' ( %s.tex ' % path)
            tex.input(codecs.open(path, 'r', encoding))
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nProblem opening file "%s"', path)
            status.info(' ) ')
        return []

class include(input):
    pass

class includeonly(Command):
    args = '@files:str'
    def invoke(self, tex):
        for file in self.parse(tex)['files']:
            tex.input(tex.kpsewhich(file))
        return []

class filecontents(Environment):
    args = 'file:str'

class FileContentsStar(Environment):
    macroName = 'filecontents*'
    args = 'file:str'

class listfiles(Command):
    pass

class typeout(Command):
    args = 'message:str'
    def invoke(self, tex):
        log.info(self.parse(tex)['message'])

class typein(Command):
    args = '[ command:str ] message'
    def invoke(self, tex):
        log.info(self.parse(tex)['message'])
        
