#!/usr/bin/env python

"""
C.9 Figures and Other Floating Bodies (p196)

"""

from plasTeX import Command, Environment, subclasses
from plasTeX import GlueCommand, DimenCommand
from plasTeX.Logging import getLogger


class Caption(Command):
    args = '[ toc ] self'
    blockType = True
    # Is the caption attached to an object?
    attached = False

    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.title = self.captionName
        return res

#
# C.9.1 Figures and Tables
#

class Float(Environment):
    blockType = True
    forcePars = True
    args = '[ loc:str ]'
    
    # List of possible caption node names.  Subclasses of Caption
    # are automatically included
    captions = []
    
    # List of macros that can have a caption
    captionable = ['picture','verbatim','listing','includegraphics','tabular'
                   'tabularx','tabular*','longtable','alltt']
    
    def digest(self, tokens):
        res = Environment.digest(self, tokens)
        # Get the names of all caption macros
        captionsubs = [x.__name__ for x in subclasses(Caption)] + self.captions
        # Apply captions to objects
        if captionsubs and self.captionable and self.macroMode == self.MODE_BEGIN:
            captions = self.getElementsByTagName(captionsubs)
            objects = self.getElementsByTagName(self.captionable)
            if len(captions) == 1:
                captions[0].attached = True
                self.title = captions[0]
            if len(captions) == len(objects):
                while captions and objects:
                    captions[0].attached = True
                    objects.pop(0).title = captions.pop(0)
        return res

class figure(Float):
    class caption(Caption):
        counter = 'figure'

class FigureStar(figure):
    macroName = 'figure*'

class table(Float):
    captionable = ['tabular','tabularx','tabular*','longtable']
    class caption(Caption):
        counter = 'table'

class TableStar(table):
    macroName = 'table*'

class suppressfloats(Command):
    pass

# Counters

class topfraction(Command):
    unicode = '0.25'

class bottomfraction(Command):
    unicode = '0.25'

class textfraction(Command):
    unicode = '0.25'

class floatpagefraction(Command):
    unicode = '0.25'

class dbltopfraction(Command):
    unicode = '0.25'

class dblfloatpagefraction(Command):
    unicode = '0.25'

class floatsep(GlueCommand):
    value = GlueCommand.new(0)

class textfloatsep(GlueCommand):
    value = GlueCommand.new(0)

class intextsep(GlueCommand):
    value = GlueCommand.new(0)

class dblfloatsep(GlueCommand):
    value = GlueCommand.new(0)

class dbltextfloatsep(GlueCommand):
    value = GlueCommand.new(0)


#
# C.9.2 Marginal Notes
#

class marginpar(Command):
    args = '[ left ] right'

class reversemarginpar(Command):
    pass

class normalmarginpar(Command):
    pass

# Style Parameters

class marginparwidth(DimenCommand):
    value = DimenCommand.new(0)

class marginparsep(DimenCommand):
    value = DimenCommand.new(0)

class marginparpush(DimenCommand):
    value = DimenCommand.new(0)
