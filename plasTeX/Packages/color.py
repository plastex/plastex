#!/usr/bin/env python

from plasTeX import Command, Environment

class textcolor(Command):
    args = 'color self'
    def invoke(self, tex):
        self.parse(tex)
        self.style['color'] = '#%s' % self.attributes['color']

class color(Environment):
    args = 'color'
    def invoke(self, tex):
        self.parse(tex)
        self.style['color'] = '#%s' % self.attributes['color']
