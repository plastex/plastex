#!/usr/bin/env python

"""
C.6.1 Quotations and Verse (p184)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger


class quote(Environment): 
    pass

class quotation(Environment):
    pass

class verse(Environment):
    pass
