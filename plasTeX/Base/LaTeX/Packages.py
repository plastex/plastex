#!/usr/bin/env python

"""
C.5 Classes, Packages, and Page Styles (p176)

"""

from plasTeX import Command, Environment
from plasTeX import Dimen, dimen
from plasTeX.Logging import getLogger

# Put the plasTeX packages into the path
import sys, os
from plasTeX import packages
sys.path.append(os.path.dirname(packages.__file__))
del packages

log = getLogger()
status = getLogger('status')

class PackageLoader(Command):

    def load(self, tex, file, options={}):
        # See if it has already been loaded
        if tex.context.packages.has_key(file):
            return

        try: 
            # Try to import a Python package by that name
            m = __import__(file, globals(), locals())
            status.info(' ( %s ' % m.__file__)
            tex.context.importMacros(vars(m))
            tex.context.packages[file] = options
            status.info(' ) ')
            return

        except ImportError, msg:
            # No Python module
            if 'No module' in str(msg):
                pass
                # Failed to load Python package
                log.warning('No Python version of %s was found' % file)
            # Error while importing
            else:
                raise

        path = tex.kpsewhich(file)

        if not path:
            log.warning('Could not find file for package "%s"' % file)
            return

        # Try to load the actual LaTeX style file
        status.info(' ( %s ' % path)

        try:
            file = open(path, 'r')
            # Put `self` in as a flag so that we can parse past our own
            # package tokens and throw them away, we don't want them in
            # the output document.
            tex.pushtoken(self)
            tex.input(file)
            tex.context.packages[file] = options
            for tok in tex:
                if tok is self:
                    break

        except (OSError, IOError, TypeError):
            # Failed to load LaTeX style file
            log.warning('Error opening package "%s"' % file)

        status.info(' ) ')

#
# C.5.1 Document Class
#

class documentclass(PackageLoader):
    args = '[ options:dict ] name:str'

    def invoke(self, tex):
        a = self.parse(tex)
        self.load(tex, a['name'], a['options'])

class documentstyle(documentclass):
    pass

#
# Style Parameters
#

class bibindent(Dimen):
    value = dimen(0)

class columnsep(Dimen):
    value = dimen(0)

class columnseprule(Dimen):
    value = dimen(0)

class mathindent(Dimen):
    value = dimen(0)

#
# C.5.2 Packages
#

class usepackage(PackageLoader):
    args = '[ options:dict ] names:list:str'
    
    def invoke(self, tex):
        a = self.parse(tex)
        for file in a['names']:
            self.load(tex, file, a['options'])

class RequirePackage(usepackage):
    pass

#
# C.5.3 Page Styles
#

class pagestyle(Command):
    args = 'style:str'

class thispagestyle(pagestyle):
    pass

class markright(Command):
    args = 'text'

class markboth(Command):
    args = 'left right'

class pagenumbering(Command):
    args = 'style:str'

class twocolumn(Command):
    args = '[ text ]'

class onecolumn(Command):
    pass

#
# Style Parameters
#

# Figure C.3: Page style parameters

class paperheight(Dimen):
    value = dimen('11in')

class paperwidth(Dimen):
    value = dimen('8.5in')

class oddsidemargin(Dimen):
    value = dimen('1in')

class evensidemargin(Dimen):
    value = dimen('1in')

class textheight(Dimen):
    value = dimen('9in')

class textwidth(Dimen):
    value = dimen('6.5in')

class topmargin(Dimen):
    value = dimen(0)

class headheight(Dimen):
    value = dimen('0.5in')

class headsep(Dimen):
    value = dimen('0.25in')

class footskip(Dimen):
    value = dimen('0.5in')

class marginparsep(Dimen):
    value = dimen('0.25in')

class marginparwidth(Dimen):
    value = dimen('0.75in')

class topskip(Dimen):
    value = dimen(0)

#
# C.5.4 The Title Page and Abstract
#

class maketitle(Command):
    pass

class title(Command):
    args = 'text'

class author(Command):
    args = 'names'

class date(Command):
    args = 'text'

class thanks(Command):
    args = 'text'

class abstract(Environment):
    pass

class titlepage(Environment):
    pass
