#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment
from array import Array

class math(Environment): 
    def __repr__(self): 
        if self.children is not None:
            return '$%s$' % reprchildren(self)
        return ''

class displaymath(math):
    block = True
    def __repr__(self):
        if self.children is not None:
            return '$$%s$$' % reprchildren(self)
        return ''

class eqnarray(Array):
    block = True

class x_eqnarray(eqnarray): 
    texname = 'eqnarray*'
