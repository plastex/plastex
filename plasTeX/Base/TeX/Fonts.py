#!/usr/bin/env python

"""
B.4 Font Information

"""

from plasTeX import Command, Environment, StringCommand

class magstephalf(StringCommand):
    value = '1095 '

class magstep(Command):
    args = 'value:Number'

class Font(Environment):
    pass

class tenrm(Font):
    pass

class sevenrm(Font):
    pass

class teni(Font):
    pass

class seveni(Font):
    pass

class tensy(Font):
    pass

class tenbf(Font):
    pass

class sevenbf(Font):
    pass

class tensl(Font):
    pass

class tentt(Font):
    pass

class tenit(Font):
    pass

class rm(Font):
    pass

class cal(Font):
    pass

class it(Font):
    pass

class sl(Font):
    pass

class bf(Font):
    pass

class tt(Font):
    pass

