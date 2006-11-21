#!/usr/bin/env python

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.LaTeX.Math import EqnarrayStar, equation, eqnarray

class pmatrix(Array):
    pass

class AlignStar(EqnarrayStar):
    """ AMSMath """
    macroName = 'align*'

class align(eqnarray):
    """ AMSMath """
    pass

