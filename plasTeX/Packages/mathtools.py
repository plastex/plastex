from plasTeX.Logging import getLogger
from plasTeX.Packages.amsmath import eqnarray, EqnarrayStar
from plasTeX.Base.LaTeX.Math import EqnarrayStar, eqnarray
from plasTeX.Base.LaTeX.Arrays import Array

getLogger().warning('Package mathtools is not well supported by plasTeX or mathjax - please contribute.')

# Hack for removing "intertext" somewhat okayish. Alignment is still lost though, would need mathjax support!
# also, the text in intertext may be double escaped.
from plasTeX import Command, sourceChildren, sourceArguments
from plasTeX.Base.LaTeX.Math import MathEnvironment
class intertext(Command):
    args = 'self'
    mathMode = False

    @property
    def source(self):
        node = self.parentNode
        while node and not isinstance(node, MathEnvironment): node = node.parentNode
        if node: return u"\\end{{{0}}}\n{1}\n\\begin{{{0}}}{2}".format(node.tagName, str(self), sourceArguments(node))
        return Command.source(self) # fallback

class shortintertext(Command):
    args = 'self'
    mathMode = False

    @property
    def source(self):
        node = self.parentNode
        while node and not isinstance(node, MathEnvironment): node = node.parentNode
        if node: return u"\\end{{{0}}}\n{1}\n\\begin{{{0}}}{2}".format(node.tagName, str(self), sourceArguments(node))
        return Command.source(self) # fallback

class casesStar(EqnarrayStar):
    macroName = "cases*"

class rcases(eqnarray):
    pass

class RCasesStar(EqnarrayStar):
    macroName = "rcases*"

class dcases(eqnarray):
    pass

class DCasesStar(EqnarrayStar):
    macroName = "dcases*"

class drcases(eqnarray):
    pass

class DRCasesStar(EqnarrayStar):
    macroName = "drcases*"

class smallmatrix(Array):
    pass

class SmallMatrixStar(Array):
    macroName = "smallmatrix*"

class bsmallmatrix(Array):
    pass

class bSmallMatrixStar(Array):
    macroName = "bsmallmatrix*"

class Bsmallmatrix(Array):
    pass

class BSmallMatrixStar(Array):
    macroName = "Bsmallmatrix*"

class vsmallmatrix(Array):
    pass

class vSmallMatrixStar(Array):
    macroName = "vsmallmatrix*"

class Vsmallmatrix(Array):
    pass

class VSmallMatrixStar(Array):
    macroName = "Vsmallmatrix*"

class bMatrixStar(Array):
    macroName = "bmatrix*"

class BMatrixStar(Array):
    macroName = "Bmatrix*"

class vMatrixStar(Array):
    macroName = "vmatrix*"

class VMatrixStar(Array):
    macroName = "Vmatrix*"
