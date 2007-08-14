#!/usr/bin/env python

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.LaTeX.Math import EqnarrayStar, equation, eqnarray
#### Imports Added by Tim ####
from plasTeX.Base.LaTeX.Math import math

class pmatrix(Array):
    pass

class _AMSEquation(eqnarray):
    pass

class _AMSEquationStar(EqnarrayStar):
    macroName = None

class align(_AMSEquation):
    pass

class AlignStar(_AMSEquationStar):
    macroName = 'align*'

class gather(_AMSEquation):
    pass

class GatherStar(_AMSEquationStar):
    macroName = 'gather*'

class falign(_AMSEquation):
    pass

class FAlignStar(_AMSEquationStar):
    macroName = 'falign*'

class multiline(_AMSEquation):
    pass

class MultilineStar(_AMSEquationStar):
    macroName = 'multiline*'

class alignat(_AMSEquation):
    pass

class AlignatStar(_AMSEquationStar):
    macroName = 'alignat*'

class split(_AMSEquation):
    pass

#### Added by Tim ####
class EquationStar(_AMSEquationStar):
    macroName = 'equation*'

class aligned(_AMSEquation):
    pass

class cases(_AMSEquation):
    pass

class alignat(_AMSEquation):
    args = 'column:int'
class AlignatStar(_AMSEquationStar):
    args = 'column:int'
    macroName = 'alignat*'

class flalign(_AMSEquation):
    pass
class FlalignStar(_AMSEquationStar):
    macroName = 'flalign*'

class subequations(_AMSEquation):
    pass

class xalignat(alignat):
    pass

class multline(multiline):
    pass
class MultlineStar(MultilineStar):
    macroName = 'multline*'

class matrix(Array):
    pass

class vmatrix(Array):
    pass
class Vmatrix(Array):
    pass

class bmatrix(Array):
    pass
class Bmatrix(Array):
    pass

#### Inline Math
class smallmatrix(math):
    pass

class dddot(math):
    pass

class ddddot(math):
    pass

