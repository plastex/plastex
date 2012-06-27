#!/usr/bin/env python

"""
B.5 Macros for text

"""

from plasTeX import Command, Environment, sourceChildren

class frenchspacing(Command):
    unicode = u''

class nonfrenchspacing(Command):
    unicode = u''

class normalbaselines(Command):
    unicode = u''

class lq(Command):
    unicode = unichr(8216)

class rq(Command):
    unicode = unichr(8217)

class lbrack(Command):
    unicode = u'['

class rbrack(Command):
    unicode = u']'

class space(Command):
    unicode = u' '

class empty(Command):
    unicode = u''

class null(Command):
    unicode = u''

class bgroup(Command):

    def invoke(self, tex):
        self.ownerDocument.context.push()

    def digest(self, tokens):
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.nodeType == Command.ELEMENT_NODE:
                if item.level < self.ENDSECTIONS_LEVEL:
                    tokens.push(item)
                    break
                if isinstance(item, (egroup,endgroup)):
                    self.endit = True
                    break
                if item.contextDepth < self.contextDepth:
                    tokens.push(item)
                    break
                item.parentNode = self
                item.digest(tokens)
            self.appendChild(item)
        self.paragraphs(force=False)

    @property
    def source(self):
        if self.hasChildNodes():
            return '{%s}' % sourceChildren(self)
        elif hasattr(self, 'endit'):
            return '{}'
        return '{'

class begingroup(bgroup):
    pass

class egroup(Command):
    unicode = u''

    def invoke(self, tex):
        self.ownerDocument.context.pop()

    @property
    def source(self):
        return '}'

    def digest(self, tokens):
        return

class endgroup(egroup):
    unicode = u''

class obeyspaces(Command):
    unicode = u''

class loop(Command):
    args = 'var:Tok'
    unicode = u''

class iterate(Command):
    unicode = u''

class repeat(Command):
    unicode = u''

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
    unicode = u''

class allowbreak(Command):
    unicode = u''

class ControlSpace(Command):
    macroName = 'active::~'

class slash(Command):
    pass

class filbreak(Command):
    pass

class goodbreak(Command):
    pass

class eject(Command):
    unicode = u''

class supereject(Command):
    unicode = u''

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
    args = 'self'

class llap(Command):
    args = 'self'

class centerline(Command):
    args = 'self'

class underbar(Command):
    args = 'self'

class hang(Command):
    pass

class textindent(Command):
    args = 'self'

class narrower(Command):
    pass

class raggedright(Environment):
    pass

#
# Accents are done in the LaTeX package
#

class dots(Command):
    unicode = unichr(8230)
