#!/usr/bin/env python

"""
C.11.2 Cross-References (p209)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger


class label(Command):
    args = 'label:id'

class ref(Command):
    args = 'label:idref'

class pageref(Command):
    args = 'label:idref'
