#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment
from array import Array

class math(Environment): 
    def __repr__(self): return '$'

class displaymath(math):
    block = True
    def __repr__(self): return '$$'

class eqnarray(Array):
    block = True
    def __repr__(self): return Environment.__repr__(self)

class x_eqnarray(eqnarray): 
    texname = 'eqnarray*'
