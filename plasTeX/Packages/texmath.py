#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment
from array import Array

class math(Environment): 
    def __repr__(self): 
        if self.childNodes:
            return '$%s$' % reprchildren(self)
        return '$'

class displaymath(math):
    def __repr__(self):
        if self.childNodes:
            return '$$%s$$' % reprchildren(self)
        return '$$'

class eqnarray(Array): pass

class x_eqnarray(eqnarray): 
    macroName = 'eqnarray*'
