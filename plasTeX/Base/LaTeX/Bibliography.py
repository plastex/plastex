#!/usr/bin/env python

"""
C.11.3 Bibliography and Citation (p208)

"""

from plasTeX import Command, Environment
from Lists import List
from plasTeX.Logging import getLogger

class bibliography(Command):
    args = 'files:str'
    
class thebibliography(List):
    args = 'widelabel'
  
    class bibitem(List.item):
        args = '[ label ] key'

class cite(Command):
    args = '[ text ] key'

class nocite(Command):
    arsg = 'keys:str'
