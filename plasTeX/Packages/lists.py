#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command, Token

class List(Environment):
    """ Base class for all list-based environments """

    class item(Command):
        args = '[ term ]'

        def digest(self, tokens):
            """
            Items should absorb all of the content within that 
            item, not just the `[...]' argument.  This is 
            more useful for the resulting document object.

            """
            self.childNodes = []
            # Absorb the tokens that belong to us
            for tok in tokens:
                if tok.nodeType == Node.ELEMENT_NODE:
                    # Hit next item in the list...
                    if type(tok) is type(self):
                        tokens.push(tok)
                        break
                    tok.digest(tokens)
                if tok.contextDepth < self.contextDepth:
                    tokens.push(tok)
                    break
                self.childNodes.append(tok)
                tok.parentNode = self

    def digest(self, tokens):
        # Drop any whitespace before the first item
        for tok in tokens:
            if tok.catcode == Token.CC_SPACE or tok.nodeName == 'par':
                continue
            tokens.push(tok)
            break
        Environment.digest(self, tokens) 
    
class description(List): pass
class _list(List): macroName = 'list'
class itemize(List): pass
class enumerate(List): pass
