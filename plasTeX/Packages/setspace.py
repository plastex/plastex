#!/usr/bin/env python

from plasTeX import IgnoreCommand, Environment

class doublespacing(IgnoreCommand):
    pass

class singlespacing(IgnoreCommand):
    pass

class onehalfspacing(IgnoreCommand):
    pass

class setstretch(IgnoreCommand):
    args = 'size:nox'
