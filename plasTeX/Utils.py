#!/usr/bin/env python

import os
from Node import Node

def reprchildren(o): return ''.join([repr(x) for x in o.childNodes])
def reprarguments(o): return o.argsource
def ismacro(o): return hasattr(o, 'macroName')
def issection(o): return level > Node.DOCUMENT_LEVEL and level < Node.ENVIRONMENT_LEVEL 
def isenv(o): return level == Node.ENVIRONMENT_LEVEL
def macroname(o):
     if o.macroName is None:
         if type(o) is type:
             return o.__name__
         return type(o).__name__
     return o.macroName

def paragraphs(toklist, par, allow_single=False):
    """ Group content into paragraphs """
    current = par()
    newlist = [current]
    for item in iter(toklist):
        if isinstance(item, par):
            newlist.append(item)
            current = item
        elif isblock(item):
            newlist.append(item)
            current = par()
            newlist.append(current)
        elif issection(item):
            newlist.append(item)
        else:
            current.append(item)

    # Filter out empty paragraphs
    final = []
    while newlist:
        item = newlist.pop(0)
        if isinstance(item, par):
            if not item:
                pass
            elif len(item) == 1 and isinstance(item[0], basestring) \
               and not item[0].strip():
                pass
            else:
                final.append(item)
        else:
            final.append(item)
 
    # If we aren't going to allow single paragrahs, pop the content
    # up one level
    if not allow_single:
        if len(final) == 1 and isinstance(final[0], par):
            return final[0]

    return final

PLASTEXINPUTS = '.'

def kpsewhich(name):
    extensions = ['.sty','.tex','.cls']
    for path in PLASTEXINPUTS.split(':'):
       for ext in extensions:
           fullpath = os.path.join(path, name+ext)
           if os.path.isfile(fullpath):
               return fullpath
    raise OSError, name

