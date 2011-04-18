#!/usr/bin/env python

import new
from plasTeX.Base import Command, verb

class url(Command):
    args = 'url:url'

class urldef(Command):
    args = 'name:cs type:cs'

    class DefinedURL(Command):
        result = None
        def invoke(self, tex):
            return self.result

    def invoke(self, tex):
        Command.invoke(self, tex)
        name = str(self.attributes['name'])
        type = str(self.attributes['type'])
        c = self.ownerDocument.context
        obj = c[type]()
        obj.parentNode = self.parentNode
        obj.ownerDocument = self.ownerDocument
        result = obj.invoke(tex)
        c.addGlobal(name, new.classobj(name, (self.DefinedURL,), {'result':result}))

class urlstyle(Command):
    args = 'style:str'

class DeclareUrlCommand(Command):
    args = 'name:cs style'
    def invoke(self, tex):
        Command.invoke(self, tex)
        name = str(self.attributes['name'])
        c = self.ownerDocument.context
        c.addGlobal(name, new.classobj(name, (url,), {}))
