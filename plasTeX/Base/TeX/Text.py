#!/usr/bin/env python

"""
B.5 Macros for text

"""

from plasTeX import Command, Environment, StringCommand, sourcechildren

class frenchspacing(Command):
    pass

class nonfrenchspacing(Command):
    pass

class normalbaselines(Command):
    pass

class lq(StringCommand):
    value = '`'

class rq(StringCommand):
    value = "'"

class lbrack(StringCommand):
    value = '['

class rbrack(StringCommand):
    value = ']'

class space(StringCommand):
    value = ' '

class empty(StringCommand):
    value = ''

class null(StringCommand):
    value = ''

class bgroup(Command):

    def invoke(self, tex):
        tex.context.push()

    def digest(self, tokens):
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.nodeType == Command.ELEMENT_NODE:
                if isinstance(item, (egroup,endgroup)):
                    break
                item.digest(tokens)
            self.appendChild(item)
        self.paragraphs()

    def source(self):
        if self.hasChildNodes():
            return '{%s}' % sourcechildren(self)
        return '{'
    source = property(source)

class begingroup(bgroup):
    pass

class egroup(Command):

    def invoke(self, tex):
        tex.context.pop()

    def source(self):
        return '}'
    source = property(source)

    def digest(self, tokens):
        return

class endgroup(egroup):
    pass

class obeyspaces(Command):
    pass

class loop(Command):
    args = 'var:Tok'

class iterate(Command):
    pass

class repeat(Command):
    pass

class enskip(Command):
    pass

class enspace(Command):
    pass

class quad(Command):
    pass

class qquad(Command):
    pass

class thinspace(Command):
    pass

class negthinspace(Command):
    pass

class hglue(Command):
    pass

class vglue(Command):
    pass

class topglue(Command):
    pass

class nointerlineskip(Command):
    pass

class offinterlineskip(Command):
    pass

class smallskip(Command):
    pass

class medskip(Command):
    pass

class bigskip(Command):
    pass

class TeXBreak(Command):
    macroName = 'break'

class allowbreak(Command):
    pass

class ControlSpace(Command):
    macroName = 'active::~'

class slash(Command):
    pass

class filbreak(Command):
    pass

class goodbreak(Command):
    pass

class eject(Command):
    pass

class supereject(Command):
    pass

class removelastskip(Command):
    pass

class smallbreak(Command):
    pass

class medbreak(Command):
    pass

class bigbreak(Command):
    pass

class line(Command):
    pass

class leftline(Command):
    args = 'text'

class llap(Command):
    args = 'text'

class centerline(Command):
    args = 'text'

class underbar(Command):
    args = 'text'

class hang(Command):
    pass

class textindent(Command):
    args = 'text'

class narrower(Command):
    pass

class raggedright(Environment):
    pass

#
# Accents are done in the LaTeX package
#


