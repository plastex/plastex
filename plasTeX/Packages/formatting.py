#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command

class center(Environment):
    block = True

class it(Environment): pass

class tt(Environment): pass

class itshape(Environment): pass

class bf(Environment): pass

class bfseries(Environment): pass

class emph(Environment): pass

class em(emph): pass

class strong(Command):
    args = 'self'

class small(Environment): pass

class sf(Environment): pass

class textit(Command):
    args = 'self'

class texttt(Command):
    args = 'self'

class textbf(Command):
    args = 'self'

class textrm(Command):
    args = 'self'
