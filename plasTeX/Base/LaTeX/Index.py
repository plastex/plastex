#!/usr/bin/env python

"""
C.11.5 Index and Glossary (p211)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger

class theindex(Environment):
    pass

class printindex(Command):
    pass

class makeindex(Command):
    pass

class makeglossary(Command):
    pass

class index(Command):
    args = 'entry:nox'

class glossary(Command):
    args = 'entry:nox'
