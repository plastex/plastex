#!/usr/bin/env python

"""
C.10.2 The array and tabular Environments

"""

import new, sys
from plasTeX import Macro, Environment, Command, StringCommand, sourcechildren
from plasTeX import Dimen, dimen

class ColumnType(Macro):

    columnAttributes = {}
    columnTypes = {}

    def __init__(self, *args, **kwargs):
        Macro.__init__(self, *args, **kwargs)
        self.style.update(self.columnAttributes)
        
    def new(cls, name, attributes, args='', before=[], after=[], between=[]):
        """
        Generate a new column type definition

        Required Arguments:
        name -- name of the column type
        attributes -- dictionary of style attributes for this column

        Keyword Arguments:
        args -- argument description string
        before -- tokens to insert before this column
        after -- tokens to insert after this column

        """
        newclass = new.classobj(name, (cls,), 
            {'columnAttributes':attributes, 'args':args,
             'before':before, 'after':after, 'between':between})
        cls.columnTypes[name] = newclass
    new = classmethod(new)

    def __repr__(self):
        return '%s: %s' % (type(self).__name__, self.style)

ColumnType.new('r', {'text-align':'right'})
ColumnType.new('c', {'text-align':'center'})
ColumnType.new('l', {'text-align':'left'})
ColumnType.new('p', {'text-align':'left'}, args='width:str')
ColumnType.new('d', {'text-align':'right'}, args='delim:str')


class Array(Environment):
    """
    Base class for all array-like structures

    """

    colspec = None

    class caption(Command):
        """ Table caption """
        args = '* [ toc ] title'
        labelable = True
        counter = 'table'

    class CellDelimiter(Command):
        """ Cell delimiter """
        macroName = 'active::&'
        def invoke(self, tex):
            # Pop and push a new context for each cell, this keeps
            # any formatting changes from the previous cell from
            # leaking over into the next cell
            tex.context.pop()
            tex.context.push()
            # Add a phantom cell to absorb the appropriate tokens
            return [self, Array.ArrayCell()]

    class EndRow(Command):
        """ End of a row """
        macroName = '\\'
        args = '* [ space ]'

        def invoke(self, tex):
            # Pop and push a new context for each row, this keeps
            # any formatting changes from the previous row from
            # leaking over into the next row
            tex.context.pop()
            self.parse(tex)
            tex.context.push()
            # Add a phantom row and cell to absorb the appropriate tokens
            return [self, Array.ArrayRow(), Array.ArrayCell()]

    class BorderCommand(Command):
        """
        Base class for border commands

        """
        BORDER_BEFORE = 0
        BORDER_AFTER  = 1

        position = BORDER_BEFORE

        def applyBorders(self, cells, location=None):
            """
            Apply borders to the given cells

            Required Arguments:
            location -- place where the border should be applied. 
                This should be 'top', 'bottom', 'left', or 'right'
            cells -- iterable containing cell instances to apply
                the borders

            """
            # Find out if the border should start and stop, or just 
            # span the whole table.
            a = self.attributes
            if a and a.has_key('span'):
                try: start, end = a['span']
                except TypeError: start = end = a['span']
            else:
                start = -sys.maxint
                end = sys.maxint
            # Determine the position of the border
            if location is None:
                location = self.locations[self.position]
            colnum = 1
            for cell in cells:
                if colnum < start or colnum > end:
                    colnum += 1
                    continue
                cell.style['border-%s-style' % location] = 'solid'
                cell.style['border-%s-color' % location] = 'black'
                cell.style['border-%s-width' % location] = '1px'
                if cell.attributes:
                    colnum += cell.attributes.get('colspan', 1)
                else:
                    colnum += 1

    class hline(BorderCommand):
        """ Full horizontal line """
        locations = ('top','bottom')

    class vline(BorderCommand):
        """ Vertical line """
        locations = ('left','right')

    class cline(hline):
        """ Partial horizontal line """
        args = 'span:list(-):int'

    class ArrayRow(Macro):
        """ Table row class """
        endtoken = None

        def digest(self, tokens):
            # Absorb tokens until the end of the row
            self.endtoken = self.digestUntil(tokens, Array.EndRow)
            if self.endtoken is not None:
                tokens.next()
                self.endtoken.digest(tokens)

        def source(self):
            if self.endtoken is not None:
                return sourcechildren(self) + self.endtoken.source
            return sourcechildren(self)
        source = property(source)

        def applyBorders(self, tocells=None, location=None):
            """ 
            Apply borders to every cell in the row 

            Keyword Arguments:
            row -- the row of cells to apply borders to.  If none
               is given, then use the current row

            """
            if tocells is None:
                tocells = self
            for cell in self:
                horiz, vert = cell.borders
                # Horizontal borders go across all columns
                for border in horiz: 
                    border.applyBorders(tocells, location=location)
                # Vertical borders only get applied to the same column
                for applyto in tocells:
                    for border in vert:
                        border.applyBorders([applyto], location=location)

        def isBorderOnly(self):
            """ Does this row exist only for applying borders? """
            for cell in self:
                if not cell.isBorderOnly:
                    return False
            return True
        isBorderOnly = property(isBorderOnly)

    class ArrayCell(Macro):
        """ Table cell class """
        endtoken = None

        def digest(self, tokens):
            self.endtoken = self.digestUntil(tokens, (Array.CellDelimiter, 
                                                      Array.EndRow))
            if isinstance(self.endtoken, Array.CellDelimiter):
                tokens.next()
                self.endtoken.digest(tokens)
            else:
                self.endtoken = None

            # Check for multicols
            for item in self:
                if item.attributes and item.attributes.has_key('colspan'):
                    self.attributes['colspan'] = item.attributes['colspan']
                if hasattr(item, 'colspec'):
                    self.colspec = item.colspec

            self.paragraphs()

        def borders(self):
            """
            Return all of the border control macros

            Returns:
            list of border command instances

            """
            # Use cached version if it exists
            if hasattr(self, '@borders'):
                return getattr(self, '@borders')

            horiz, vert = [], []

            # Locate the border control macros at the end of the cell
            for i in range(len(self)-1, -1, -1):
                item = self[i]
                if item.isElementContentWhitespace:
                    continue
                if isinstance(item, Array.hline):
                    item.position = Array.hline.BORDER_AFTER
                    horiz.append(item)
                    continue
                elif isinstance(item, Array.vline):
                    item.position = Array.vline.BORDER_AFTER
                    vert.append(item)
                    continue
                break

            # Locate border control macros at the beginning of the cell
            for item in self:
                if item.isElementContentWhitespace:
                    continue
                if isinstance(item, Array.hline):
                    item.position = Array.hline.BORDER_BEFORE
                    horiz.append(item)
                    continue
                elif isinstance(item, Array.vline):
                    item.position = Array.vline.BORDER_BEFORE
                    vert.append(item)
                    continue
                break

            setattr(self, '@borders', (horiz, vert))

            return horiz, vert

        borders = property(borders)

        def isBorderOnly(self):
            """ Does this cell exist only for applying borders? """
            for item in self:
                if item.isElementContentWhitespace:
                    continue
                elif isinstance(item, Array.BorderCommand):
                    continue
                return False
            return True
        isBorderOnly = property(isBorderOnly)

        def source(self):
            if self.endtoken is not None:
                return sourcechildren(self) + self.endtoken.source
            return sourcechildren(self)
        source = property(source)

    class multicolumn(Command):
        """ Column spanning cell """
        args = 'colspan:int colspec self'

        def invoke(self, tex):
            Command.invoke(self, tex)
            self.colspec = Array.compileColspec(self.attributes['colspec']).pop(0)

        def digest(self, tokens):
            Command.digest(self, tokens)
            self.paragraphs()


    def invoke(self, tex):
        if self.macroMode == Macro.MODE_END:
            tex.context.pop(self) # End of table, row, and cell
            return
        
        Environment.invoke(self, tex)

#!!!
#
# Need to handle colspec processing here so that tokens that must 
# be inserted before and after columns are known
#
#!!!
        if self.attributes.has_key('colspec'):
            self.colspec = Array.compileColspec(self.attributes['colspec'])

        tex.context.push() # Beginning of cell
        # Add a phantom row and cell to absorb the appropriate tokens
        return [self, Array.ArrayRow(), Array.ArrayCell()]

    def digest(self, tokens):
        Environment.digest(self, tokens)

        # Give subclasses a hook before going on
        self.processRows()

        self.applyBorders()

    def processRows(self):
        """
        Subcloss hook to process rows after digest

        Tables are fairly complex structures, so subclassing them
        in a useful way can be difficult.  This method was added
        simply to allow subclasses to have access to the content of a
        table immediately after the digest method.

        """
        pass

    def applyBorders(self):
        """
        Apply borders from \\(h|c|v)line and colspecs

        """
        lastrow = len(self) - 1
        emptyrows = []
        prev = None
        for i, row in enumerate(self):
            if not isinstance(row, Array.ArrayRow):
                continue
            # If the row is only here to apply borders, apply the
            # borders to the adjacent row.  Empty rows are deleted later.
            if row.isBorderOnly:
                if i == 0 and lastrow:
                    row.applyBorders(self[1], 'top')
                elif prev is not None:
                    row.applyBorders(prev, 'bottom')
                emptyrows.insert(0, i)
            else:
                row.applyBorders()
                if self.colspec:
                    # Expand multicolumns so that they don't mess up
                    # the colspec attributes
                    cells = []
                    for cell in row:
                        span = 1
                        if cell.attributes:
                            span = cell.attributes.get('colspan', 1)
                        cells += [cell] * span
                    for colspec, cell in zip(self.colspec, cells):
                        colspec = getattr(cell, 'colspec', colspec)
                        cell.style.update(colspec.style)
                prev = row

        # Pop empty rows
        for i in emptyrows:
            self.pop(i)

    def compileColspec(cls, colspec):
        """ 
        Compile colspec into an object 

        Required Arguments:
        colspec -- an unexpanded token list that contains a LaTeX colspec

        Returns:
        list of `ColumnType` instances 

        """
        output = []
        colspec = iter(colspec)
        before = None
        leftborder = None
        for item in colspec:
            if item.isElementContentWhitespace:
                continue

            if item.nodeType == item.ELEMENT_NODE: 
                continue

            if item == '|':
                if not output:
                    leftborder = True
                else:
                    output[-1].style['border-right'] = '1px solid black'
                continue

            if item in '>':
                before = colspec.next()
                continue

            if item in '<':
                output[-1].after = colspec.next()
                continue

            if item in '@':
                if output:
                    output[-1].between = colspec.next()
                continue

            if item in '*':
                num = int(colspec.next()[0])
                spec = colspec.next()[0]
                for i in range(num):
                    output.append(ColumnType.columnTypes.get(item, ColumnType)())
                continue

            output.append(ColumnType.columnTypes.get(item, ColumnType)())
            if before:
                output[-1].before = before
                before = None

        if leftborder:
            output[0].style['border-left'] = '1px solid black'
             
        return output

    compileColspec = classmethod(compileColspec)


class array(Array):
    args = '[ pos:str ] colspec'

class tabular(Array):
    args = '[ pos:str ] colspec'

class TabularStar(tabular):
    macroName = 'tabular*'
    args = 'width:dimen [ pos:str ] colspec'

# Style Parameters

class arraycolsep(Dimen):
    value = dimen(0)

class tabcolsep(Dimen):
    value = dimen(0)

class arrayrulewidth(Dimen):
    value = dimen(0)

class doublerulesep(Dimen):
    value = dimen(0)

class arraystretch(StringCommand):
    value = '1'
