#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment
from array import Array

class math(Environment): 
    def source(self): 
        if self.childNodes:
            return '$%s$' % sourcechildren(self)
        return '$'
    source = property(source)

class displaymath(math):
    def source(self):
        if self.childNodes:
            return '$$%s$$' % sourcechildren(self)
        return '$$'
    source = property(source)

class eqnarray(Array): pass

class x_eqnarray(eqnarray): 
    macroName = 'eqnarray*'
