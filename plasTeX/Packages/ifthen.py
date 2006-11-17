#!/usr/bin/env python

"""
This package is not properly implemented.  The \ifthenelse command simply
returns the 'false' portion of the command.  Hopefully, some day this will
be done properly.

"""

from plasTeX import Command

class ifthenelse(Command):
    args = 'test:nox then:nox else' 

    class _not(Command):
        macroName = 'not'

    class _and(Command):
        macroName = 'and'

    class _or(Command):
        macroName = 'or'

    class NOT(Command):
        pass

    class AND(Command):
        pass

    class OR(Command):
        pass

    class openParen(Command):
        macroName = '('

    class closeParen(Command):
        macroName = ')'

    class isodd(Command):
        args = 'number:int'

    class isundefined(Command):
        args = 'command:str'

    class equal(Command):
        args = 'first second'

    class lengthtest(Command):
        args = 'test'

    class boolean(Command):
        args = 'name:str'

class newboolean(Command):
    args = 'name:str'

class provideboolean(Command):
    args = 'name:str'

class setboolean(Command):
    args = 'name:str value:str'

class whiledo(Command):
    args = 'test:nox operations'



