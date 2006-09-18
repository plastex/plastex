#!/usr/bin/env python

import time
from plasTeX import Command

class prefacename(Command): unicode = 'Preface'
class refname(Command): unicode = 'References'
class abstractname(Command): unicode = 'Abstract'
class bibname(Command): unicode = 'Bibliography'
class chaptername(Command): unicode = 'Chapter'
class appendixname(Command): unicode = 'Appendix'
class contentsname(Command): unicode = 'Contents'
class listfigurename(Command): unicode = 'List of Figures'
class listtablename(Command): unicode = 'List of Tables'
class indexname(Command): unicode = 'Index'
class figurename(Command): unicode = 'Figure'
class tablename(Command): unicode = 'Table'
class partname(Command): unicode = 'Part'
class enclname(Command): unicode = 'encl'
class ccname(Command): unicode = 'cc'
class headtoname(Command): unicode = 'To'
class pagename(Command): unicode = 'Page'
class seename(Command): unicode = 'see'
class alsoname(Command): unicode = 'see also'
class proofname(Command): unicode = 'Proof'
class glossaryname(Command): unicode = 'Glossary'

# Added for hyperref
class sectionname(Command): unicode = 'section'
class subsectionname(Command): unicode = 'subsection'
class subsubsectionname(Command): unicode = 'subsubsection'
class paragraphname(Command): unicode = 'paragraph'
class Hfootnotename(Command): unicode = 'footnote'
class AMSname(Command): unicode = 'Equation'
class equationname(Command): unicode = 'Equation'
class theoremname(Command): unicode = 'Theorem'
class Itemname(Command): unicode = 'item'

def ukdate():
    day = time.strftime('%d')
    suffix = 'th'
    if day.endswith('1'):
        suffix = 'st'
    elif day.endswith('2'):
        suffix = 'nd'
    elif day.endswith('3'):
        suffix = 'rd'
    return time.strftime('%d'+suffix+' %B %Y')

def usdate():
    return time.strftime('%B %d, %Y')

def audate():
    return time.strftime('%d %B %Y')

class today(Command):
    unicode = usdate()
