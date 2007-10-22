#!/usr/bin/env python

from plasTeX import Environment

class sideways(Environment):
    def invoke(self, tex):
        return []
