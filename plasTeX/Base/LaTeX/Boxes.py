#!/usr/bin/env python

"""
C.13.3 Boxes (p217)

"""

from plasTeX import Command, Environment
from plasTeX import Dimen, dimen, Glue, glue
from plasTeX.Logging import getLogger

class TextBoxCommand(Command):

    class width(Dimen):
        value = dimen(0)
 
    class height(Dimen):
        value = dimen(0)

    class depth(Dimen):
        value = dimen(0)

    class totalheight(Dimen):
        value = dimen(0)


#class mbox(Command):
#    args = 'text'

class makebox(TextBoxCommand):
    args = '[ width:dimen ] [ pos:str ] self'

class fbox(Command):
    args = 'self'

class framebox(TextBoxCommand):
    args = '[ width:dimen ] [ pos:str ] self'

class newsavebox(Command):
    args = 'name:cs'

class sbox(Command):
    args = 'name:cs text'

class savebox(TextBoxCommand):
    args = 'name:cs [ width:dimen ] [ pos ] text'

class lrbox(Environment):
    args = 'name:cs'

class usebox(Command):
    args = 'name:cs'

class parbox(Command):
    args = '[ pos:str ] width:dimen self'

class minipage(Environment):
    args = '[ pos:str ] width:dimen'

class rule(Command):
    args = '[ raise:dimen ] width:dimen height:dimen'

class raisebox(TextBoxCommand):
    args = 'raise:dimen [ height:dimen ] [ depth:dimen ] self'

# Style Parameters

class fboxrule(Dimen):
    value = dimen(0)

class fboxsep(Glue):
    value = glue(0)
