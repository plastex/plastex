#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment
from plasTeX.Context import Context

class math(Environment): 
    pass

class displaymath(math):
    block = True

class eqnarray(math):
    block = True

class x_eqnarray(eqnarray): 
    texname = 'eqnarray*'
