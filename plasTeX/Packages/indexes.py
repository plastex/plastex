#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command

index        = {}
index['syn'] = []
index['sbj'] = []

class ssyni(Command):
    args = ' term1 term2 '
#   block = True
    def parse(self,tex):
        Command.parse(self,tex)
        index['syn'].append((None,
                             self.attributes['term1'], 
                             None,
                             self.attributes['term2']))


class ssbji(Command):
    args = ' term1 term2 '
#   block = True
    def parse(self,tex):
        Command.parse(self,tex)
        index['sbj'].append((None,
                             self.attributes['term1'], 
                             None,
                             self.attributes['term2']))
