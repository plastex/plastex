#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Command, Environment

class textcolor(Command):
    args = 'color self'
    def parse(self, tex):
        Command.parse(self, tex)
        self.style['color'] = '#%s' % self.attributes['color']
        return self

class color(Environment):
    args = 'color'
    def parse(self, tex):
        Environment.parse(self, tex)
        self.style['color'] = '#%s' % self.attributes['color']
        return self
