#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command

class List(Environment):
    """ Base class for all list-based environments """

    block = True

    class item(Command):
        args = '[ term ]'

class description(List): pass
class _list(List): texname = 'list'
class itemize(List): pass
class enumerate(List): pass
