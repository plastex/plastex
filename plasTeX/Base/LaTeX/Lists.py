#!/usr/bin/env python

"""
C.6.2 List-Making Environments
C.6.3 The list and trivlist Enviroments

"""

from plasTeX import Environment, Command, Counter, TheCounter
from plasTeX import Dimen, dimen
from plasTeX import Logging

log = Logging.getLogger()

class List(Environment):
    """ Base class for all list-based environments """
    depth = 0
    counters = ['enumi','enumii','enumiii','enumiv']

    class item(Command):
        args = '[ term ]'
        counter = 'enumi'
        position = 0

        def invoke(self, tex):
            """ Set up counter for this list depth """
            try:
                self.counter = List.counters[List.depth-1]
                self.position = tex.context.counters[self.counter].value + 1
            except (KeyError, IndexError):
                pass
            return Command.invoke(self, tex)

        def digest(self, tokens):
            """
            Items should absorb all of the content within that 
            item, not just the `[...]' argument.  This is 
            more useful for the resulting document object.

            """
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                tokens.push(tok)
                break
            self.digestUntil(tokens, type(self))
            self.paragraphs()

    def invoke(self, tex):
        """ Set list nesting depth """
        if self.macroMode != Environment.MODE_END:
            List.depth += 1
        else:
            List.depth -= 1
        try:
            for i in range(List.depth+1, len(List.counters)):
                tex.context.counters[List.counters[i]].setcounter(0)
        except (IndexError, KeyError):
            pass
        return Environment.invoke(self, tex)

    def digest(self, tokens):
        # Drop any whitespace before the first item
        for tok in tokens:
            if tok.isElementContentWhitespace:
                continue
#           if tok.nodeName != 'item':
#               log.warning('dropping non-item from beginning of list')
#               continue
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
    args = 'defaultlabel decls:nox'

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
