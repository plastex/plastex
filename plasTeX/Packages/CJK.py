#!/usr/bin/env python

from plasTeX import Command, Environment

class CJK(Environment):
    args = 'encoding args'
    def invoke(self, tex):
        Environment.parse(self, tex)
        return []
