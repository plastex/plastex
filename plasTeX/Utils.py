#!/usr/bin/env python

import sys, os, new

DOCUMENT = -sys.maxint
VOLUME = -1
PART = 0
SECTION = 1
SUBSECTION = 2
SUBSUBSECTION = 3
PARAGRAPH = 4
SUBPARAGRAPH = 5
SUBSUBPARAGRAPH = 6
ENVIRONMENT = 10
PARAGRAPH = 100
COMMAND = 200

def classname(obj):
    if type(obj) is type:
        return obj.__name__
    else:
        return type(obj).__name__

def ismacro(obj):
    """ Is the given object a valid macro? """   
    return hasattr(obj, 'texname')

def xmlstr(obj):
    """ Escape special characters to create a legal xml string """
    if isinstance(obj, basestring):
        return obj.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    else:
        return str(obj)

def isblock(tok):
    """ Is this token a block-level macro? """
    return getattr(type(tok), 'block', False)

def issection(tok):
    """ Is this token a section? """
    level = getattr(type(tok), 'level', None)
    if level is None:
        return False
    return level > DOCUMENT and level < ENVIRONMENT 

def isenv(tok):
    """ Is this token an environment? """
    return hasattr(tok, 'level') and tok.level is not None

def flatten(items, group=None):
    """ Reduce a list of lists to a flat list """
    for item in items:
        if type(item) == list:
            if group is not None:
                yield group[0]
            for j in flatten(item, group):
                yield j
            if group is not None:
                yield group[1]
        else:
            yield item

def normalize(toklist):
    """ Merge all consecutive strings """
    newtoklist = []
    merge = []
    for item in toklist:
        if item is None:
            pass
        elif isinstance(item, basestring):
            merge.append(item)
        else:
            if merge:
                newtoklist.append(''.join(merge))
                merge = []
            newtoklist.append(item)
    if merge:
        newtoklist.append(''.join(merge))
    return newtoklist


def tokens2tree(toklist):
    """ Convert a list of tokens into a document tree """
    tokens = iter(toklist)
    document = []
    for item in tokens:
        if item is None:
            continue
        if hasattr(item, 'digest'):
            item = item.digest(tokens)
            if item is not None:
                if type(item) is list:
                    document.extend(item)
                else:
                    document.append(item)
        else:
            document.append(item)
    return document


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

