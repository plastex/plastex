#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Macro, Environment, Command

class verbatim(Environment):

    def invoke(self, tex):
        """ Parse until we reach `\end{verbatim}' """
        escape = tex.context.categories[0][0]
        bgroup = tex.context.categories[1][0]
        egroup = tex.context.categories[2][0]
        tex.context.push(self)
        tex.context.setVerbatimCatcodes()
        tokens = [self]
        endpattern = list(r'%send%s%s%s' % (escape, bgroup, 
                                            self.nodeName, egroup))
        endlength = len(endpattern)
        # Iterate through tokens until the endpattern is found
        for tok in tex:
            tokens.append(tok)
            if len(tokens) >= endlength:
                if tokens[-endlength:] == endpattern:
                    tokens = tokens[:-endlength]
                    break
        end = type(self)()
        end.macroMode = Macro.MODE_END
        tokens.append(end)
        tex.context.pop(self)
        return tokens

class verb(Command):
    args = '*'

    def invoke(self, tex):
        """ Parse for matching delimiters """
        tex.context.push(self)
        self.parse(tex)
        tex.context.setVerbatimCatcodes()
        # See what the delimiter is
        for endpattern in tex:
            self.delimiter = endpattern
            break
        tokens = [self, endpattern]
        # Parse until this delimiter is seen again
        for tok in tex:
            tokens.append(tok)
            if tok == endpattern:
                break
        tex.context.pop(self)
        return tokens

    def digest(self, tokens):
        for endpattern in tokens:
            break
        for tok in tokens:
            if tok == endpattern:
                break
            self.appendChild(tok)

    def source(self):
        return '\\%s%s%s%s%s' % (self.nodeName, sourcearguments(self),
                                 self.delimiter, sourcechildren(self), 
                                 self.delimiter)
    source = property(source)

