#!/usr/bin/env python

import sys, os, new

DOCUMENT = -sys.maxint
VOLUME = -2
PART = -1
CHAPTER = 0
SECTION = 1
SUBSECTION = 2
SUBSUBSECTION = 3
PARAGRAPH = 4
SUBPARAGRAPH = 5
SUBSUBPARAGRAPH = 6
PAR = 20
ENVIRONMENT = 20
CHARACTER = COMMAND = 100

reprchildren = lambda o: ''.join([repr(x) for x in o.children])
isexpanded = lambda o: o.code > 99   # See Tokenizer.py
isinternal = lambda o: o.code > 499   # See Tokenizer.py
ismacro = lambda o: hasattr(o, 'texname')
issection = lambda o: level > DOCUMENT and level < ENVIRONMENT 
isenv = lambda o: level == ENVIRONMENT

def classname(obj):
    if type(obj) is type:
        return obj.__name__
    else:
        return type(obj).__name__

def macroname(obj):
     if obj.texname is None:
         return classname(obj)
     return obj.texname

def xmlstr(obj):
    """ Escape special characters to create a legal xml string """
    if isinstance(obj, basestring):
        return obj.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    else:
        return str(obj)

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

