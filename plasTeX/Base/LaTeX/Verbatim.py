"""
C.6.4 Verbatim

"""

from plasTeX import VerbatimEnvironment, Command, sourceArguments, sourceChildren
from plasTeX.Base.TeX.Text import bgroup
from plasTeX.Tokenizer import Other, Parameter

class verbatim(VerbatimEnvironment):
    pass

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
        # Get the delimiter: it's usually the next token, with special cases for some
        # characters.
        for endpattern in tex:
            # If the opening delimiter is a ``{`` character, parsed as a ``bgroup``
            # token, the end delimiter must be a ``}`` character.
            if isinstance(endpattern, bgroup):
                endpattern = Other('}')
            # The character # is parsed as a ``Parameter`` token when it immediately 
            # follows ``\verb``, but the corresponding end delimiter will be parsed as
            # an ``Other`` token. So if that's the case, change ``endpattern`` to an
            # ``Other`` token with the same content.
            if isinstance(endpattern, Parameter):
                endpattern = Other(str(endpattern))
            self.delimiter = endpattern
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
        endpattern = next(iter(tokens))
        for tok in tokens:
            if tok == endpattern:
                break
            self.appendChild(tok)

    @property
    def source(self):
        return '\\%s%s%s%s%s' % (self.nodeName, sourceArguments(self),
                                 self.delimiter, sourceChildren(self),
                                 self.delimiter)

    def normalize(self, charsubs=None):
        """ Normalize, but don't allow character substitutions """
        return Command.normalize(self)
