#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command

class verbatim(Environment):
    def parse(self, tex):
        self.append(tex.getVerbatim(r'\end{%s}' % self.nodeName))
        return self

class verb(Command):
    def parse(self, tex):
        self.append(tex.getVerbatim(tex.getUnexpandedArgument(), True))
        return self


