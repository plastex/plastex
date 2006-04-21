#!/usr/bin/env python

from plasTeX import Command


def initialize(context):
    # Lists
    context.newcounter('enumi')
    context.newcounter('enumii')
    context.newcounter('enumiii')
    context.newcounter('enumiv')

    # Sections
    context.newcounter('part', resetby='volume', 
                       format='%(part)s')
    context.newcounter('chapter', resetby='part', 
                       format='%(chapter)s')
    context.newcounter('section', resetby='chapter', 
                       format='%(thechapter)s.%s')
    context.newcounter('subsection', resetby='section', 
                       format='%(thesection)s.%s')
    context.newcounter('subsubsection', resetby='subsection', 
                       format='%(thesubsection)s.%s')
    context.newcounter('paragraph', resetby='subsubsection', 
                       format='%(thesubsubsection)s.%s')
    context.newcounter('subparagraph', resetby='paragraph',
                       format='%(theparagraph)s.%s')
    context.newcounter('subsubparagraph', resetby='subparagraph',
                       format='%(thesubparagraph)s.%s')

    context.newcounter('secnumdepth')
    context.newcounter('tocdepth')

    # Floats
    context.newcounter('figure', resetby='chapter', 
                       format='%(thesection)s.%s')
    context.newcounter('table', resetby='chapter',
                       format='%(thesection)s.%s')
    context.newcounter('topnumber')
    context.newcounter('bottomnumber')
    context.newcounter('totalnumber')
    context.newcounter('dbltopnumber')


class frontmatter(Command): 
    pass

class mainmatter(Command):
    pass

class backmatter(Command):
    pass
