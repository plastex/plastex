#!/usr/bin/env python

"""

"""

from plasTeX import Command, Environment


class center(Environment): 
    pass

class centering(center):
    pass

class flushleft(Environment):
    pass

class raggedright(flushleft):
    pass

class flushright(Environment):
    pass

class raggedleft(flushright):
    pass

class raggedbottom(Environment):
    pass
