#!/usr/bin/env python

"""
C.6.4 Verbatim

"""

from plasTeX import Macro, Environment, Command, sourceArguments, sourceChildren
from plasTeX.Base.TeX.Text import bgroup, egroup
from plasTeX.Tokenizer import Other

class verbatim(Environment):
    blockType = True
    captionable = True

    def invoke(self, tex):
        """ Parse until we reach `\end{verbatim}' or `\endverbatim' """
        if self.macroMode == Environment.MODE_END:
            return

        escape = self.ownerDocument.context.categories[0][0]
        bgroup = self.ownerDocument.context.categories[1][0]
        egroup = self.ownerDocument.context.categories[2][0]
        self.ownerDocument.context.push(self)
        self.parse(tex)
        self.ownerDocument.context.setVerbatimCatcodes()
        tokens = [self]

        # Should the end environment be expanded?
        expand = True

        # Get the name of the currently expanding environment
        name = self.nodeName
        if self.ownerDocument.context.currenvir is not None:
            name = self.ownerDocument.context.currenvir

        # If we were invoke by a \begin{...} look for an \end{...}
        endpattern = list(r'%send%s%s%s' % (escape, bgroup, name, egroup))

        # If we were invoked as a command (i.e. \verbatim) look
        # for an end without groupings (i.e. \endverbatim)
        endpattern2 = list(r'%send%s' % (escape, name))

        endlength = len(endpattern)
        endlength2 = len(endpattern2)
        # Iterate through tokens until the endpattern is found
        for tok in tex:
            tokens.append(tok)
            if len(tokens) >= endlength:
                if tokens[-endlength:] == endpattern:
                    tokens = tokens[:-endlength]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break
            elif len(tokens) >= endlength2:
                if tokens[-endlength2:] == endpattern2:
                    tokens = tokens[:-endlength2]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break

        return tokens

    def normalize(self, charsubs=[]):
        """ Normalize, but don't allow character substitutions """
        return Environment.normalize(self)

class endverbatim(verbatim):
    def invoke(self, tex):
        end = self.ownerDocument.createElement(self.nodeName[3:])
        end.parentNode = self.parentNode
        end.macroMode = Environment.MODE_END
        return [end]

class VerbatimStar(verbatim):
    macroName = 'verbatim*'

class EndVerbatimStar(endverbatim):
    macroName = 'endverbatim*'

class verb(Command):
    args = '*'

    def invoke(self, tex):
        """ Parse for matching delimiters """
        self.ownerDocument.context.push(self)
        self.parse(tex)
        self.ownerDocument.context.setVerbatimCatcodes()
        # See what the delimiter is
        for endpattern in tex:
            self.delimiter = endpattern
            if isinstance(endpattern, bgroup):
                self.delimiter = endpattern = Other('}')
            break
        tokens = [self, endpattern]
        # Parse until this delimiter is seen again
        for tok in tex:
            tokens.append(tok)
            if tok == endpattern:
                break
        self.ownerDocument.context.pop(self)
        return tokens

    def digest(self, tokens):
        for endpattern in tokens:
            break
        for tok in tokens:
            if tok == endpattern:
                break
            self.appendChild(tok)

    @property
    def source(self):
        return '\\%s%s%s%s%s' % (self.nodeName, sourceArguments(self),
                                 self.delimiter, sourceChildren(self), 
                                 self.delimiter)

    def normalize(self, charsubs=[]):
        """ Normalize, but don't allow character substitutions """
        return Command.normalize(self)

