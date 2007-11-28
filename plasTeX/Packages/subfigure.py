#!/usr/bin/env python

"""
subfigure package

"""

from plasTeX import Command, Environment

def ProcessOptions(options, document):
    context = document.context
    context.newcounter('subfigure', resetby='figure', 
                       format='${thefigure}.${subfigure.alph}')
    context.newcounter('subtable', resetby='table', 
                       format='${thetable}.${subtable.alph}')

class subfigurename(Command):
    unicode = ''

class subtablename(Command):
    unicode = ''

class subfigure(Command):
    args = '[ title ] self'
    counter = 'subfigure'

class subtable(Command):
    args = '[ title ] self'
    counter = 'subtable'
