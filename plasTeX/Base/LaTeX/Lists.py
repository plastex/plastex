#!/usr/bin/env python

"""
C.6.2 List-Making Environments
C.6.3 The list and trivlist Enviroments

"""

from plasTeX import Environment, Command, Counter, TheCounter
from plasTeX import Dimen, dimen

class List(Environment):
    """ Base class for all list-based environments """

    class item(Command):
        args = '[ term ]'

        def digest(self, tokens):
            """
            Items should absorb all of the content within that 
            item, not just the `[...]' argument.  This is 
            more useful for the resulting document object.

            """
            return self.digestUntil(tokens, type(self))

    def digest(self, tokens):
        # Drop any whitespace before the first item
        for tok in tokens:
            if tok.isElementContentWhitespace:
                continue
            tokens.push(tok)
            break
        Environment.digest(self, tokens) 

#
# Counters -- enumi, enumii, enumiii, enumiv
#            

Counter('enumi')
Counter('enumii')
Counter('enumiii')
Counter('enumiv')

class theenumi(TheCounter): pass
class theenumii(TheCounter): pass
class theenumiii(TheCounter): pass
class theenumiv(TheCounter): pass

# C.6.2
    
class itemize(List): 
    pass

class labelitemi(Command):
    pass
class labelitemii(Command):
    pass
class labelitemiii(Command):
    pass
class labelitemiv(Command):
    pass

class enumerate(List): 
    pass

class description(List): 
    pass

# C.6.3

class trivlist(List): 
    pass

class ConfigurableList(List):
    macroName = 'list'
    args = 'defaultlabel decls'

class topsep(Dimen):
    value = dimen(0)

class partopsep(Dimen):
    value = dimen(0)

class itemsep(Dimen):
    value = dimen(0)

class parsep(Dimen):
    value = dimen(0)

class leftmargin(Dimen):
    value = dimen(0)

class rightmargin(Dimen):
    value = dimen(0)

class listparindent(Dimen):
    value = dimen(0)

class itemindent(Dimen):
    value = dimen(0)

class labelsep(Dimen):
    value = dimen(0)

class labelwidth(Dimen):
    value = dimen(0)

class makelabel(Command):
    args = 'label'

class usecounter(Command):
    args = 'name:str'
