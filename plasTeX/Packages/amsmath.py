#!/usr/bin/env python

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.LaTeX.Math import EqnarrayStar, equation, eqnarray

class pmatrix(Array):
    pass

class _AMSEquation(eqnarray):
    pass

class _AMSEquationStar(EqnarrayStar):
    macroName = None

class align(_AMSEquation):
    pass

class AlignStar(_AMSEquation):
    macroName = 'align*'

class gather(_AMSEquation):
    macroName = None

class GatherStar(_AMSEquation):
    macroName = 'gather*'

class falign(_AMSEquation):
    pass

class FAlignStar(_AMSEquation):
    macroName = 'falign*'

class multiline(_AMSEquation):
    pass

class MultilineStar(_AMSEquation):
    macroName = 'multiline*'

class alignat(_AMSEquation):
    pass

class AlignatStar(_AMSEquation):
    macroName = 'alignat*'

class split(_AMSEquation):
    pass

