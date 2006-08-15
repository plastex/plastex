#!/usr/bin/env python

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Arrays import Array
from plasTeX.Base.LaTeX.Math import EqnarrayStar, equation

class pmatrix(Array):
    pass

class AlignStar(EqnarrayStar):
    """ AMSMath """
    macroName = 'align*'

class align(equation):
    """ AMSMath """
    pass

