#!/usr/bin/env python

from plasTeX import Command, Environment

class afterpage(Command):
    args = 'self:nox'

    def invoke(self, tex):
        super(afterpage, self).invoke(tex)
        return []
