#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command, MODE_END

Node = Command

BORDERTOP = 1
BORDERBOTTOM = 2
BORDERLEFT = 4
BORDERRIGHT = 8

class ColspecItem(Node):
    def __init__(self, data=None):
        Node.__init__(self, data)
        self.before = []
        self.after = []

class Array(Environment):

    class alignmenttab(Command):
        """ Cell delimiter """
        def invoke(self, tex):
            tex.context.pop()
            tex.context.push()
        def __repr__(self):
            return '&'

    class cr(Command):
        """ End of a row """
        texname = '\\'
        args = '* [ space ]'
        def invoke(self, tex):
            tex.context.pop()
            self.parse(tex)
            tex.context.push()
        def __repr__(self):
            return '\\\\'

    class cline(Command):
        """ Partial horizontal line """
        args = 'span:str'
        def invoke(self, tex):
            attrs = self.attributes
            self.parse(tex)
            attrs['span'] = [int(x) for x in attrs['span'].split('-')]
            if len(attrs['span']) == 1:
                attrs['span'] *= 2

    class hline(Command):
        """ Full horizontal line """

    class vline(Command):
        """ Vertical line """

    class endhead(Command):
        """ End of head section of longtable """

    class endfirsthead(Command):
        """ End of first head section of longtable """

    class endfoot(Command):
        """ End of footer section of longtable """

    class endlastfoot(Command):
        """ End of last footer section of longtable """

    class ArrayRow(Node):
        """ Class used for array rows """

    class ArrayDataCell(Node):
        """ Class used for array data cells """

    class ArrayHeaderCell(Node):
        """ Class used for array header cells """

    class ArrayFooterCell(Node):
        """ Class used for array footer cells """

    class multicolumn(Command):
        """ Column spanning cell """
        args = 'colspan:int colspec self'

    def invoke(self, tex):
        if self.mode == MODE_END:
            tex.context.pop(self) # End of table
            return 
        Environment.invoke(self, tex)
        tex.context.push() # Beginning of cell

#   def digest(self, tokens):
#       Environment.digest(self, tokens)
#       header, footer = self.getHeaderAndFooter()
#       body = self.getRowsAndCells()

#       # See if the footer is just a horizontal rule
#       if footer is type(self).hline and body:
#           for cell in body[-1]:
#               cell.style['border-bottom'] = '1px solid black'
#           footer = []

#       self[:] = header + body + footer

    def compileColspec(self, colspec):
        """ Compile colspec into an object """
        colspec = [x for x in colspec
                     if (hasattr(x, 'strip') and x.strip()) or 
                         not hasattr(x, 'strip')]

        # Strip any left borders, all other borders will be on the right
        leftborder = 0
        while colspec and colspec[0] == '|':
            leftborder = 1
            colspec.pop(0)

        output = []
        colspec = iter(colspec)
        for item in colspec:
            if item == 'r':
                output.append(ColspecItem())
                output[-1].style['text-align'] = 'right'
            elif item == 'c':
                output.append(ColspecItem())
                output[-1].style['text-align'] = 'center'
            elif item == 'l':
                output.append(ColspecItem())
            elif item == 'p':
                colspec.next() 
                output.append(ColspecItem())
            elif item == 'd':
                colspec.next() 
                output.append(ColspecItem())
            elif item == '|':
                output[-1].style['border-right'] = '1px solid black'
        if leftborder:
            output[0].style['border-left'] = '1px solid black'
             
        return output

    def getHeaderAndFooter(self):
        """ Retrieve header and footer information """
        # The footers must be stripped first
        footer = self.stripFooter()
        header = self.stripHeader()
        return header, footer

    def stripHeader(self):
        """ Strip and return longtable header content """
        types = [type(x) for x in self]

        try: endhead = types.index(type(self).endhead)
        except ValueError: endhead = -1
        try: endfirsthead = types.index(type(self).endfirsthead)
        except ValueError: endfirsthead = -1

        header = []
        if endhead > -1 and endfirsthead > -1:
            header = self[:endfirsthead]
            del self[:endhead+1]
        elif endhead > -1:
            header = self[:endhead]
            del self[:endhead]
        elif endfirsthead > -1:
            header = self[:endfirsthead]
            del self[:endfirsthead]

        return self.getRowsAndCells(header)

    def stripFooter(self):
        """ Strip and return longtable footer content """
        types = [type(x) for x in self]

        try: endhead = types.index(type(self).endhead)
        except ValueError: endhead = -1
        try: endfirsthead = types.index(type(self).endfirsthead)
        except ValueError: endfirsthead = -1
        try: endfoot = types.index(type(self).endfoot)
        except ValueError: endfoot = -1
        try: endlastfoot = types.index(type(self).endlastfoot)
        except ValueError: endlastfoot = -1

        # Retrieve footer content
        footer = []
        if endfoot > -1 and endlastfoot > -1:
            footer = self[endfoot:endlastfoot]
            start = max(endhead, endfirsthead, 0) + 1
            del self[start:endlastfoot+1]
        elif endfoot > -1:
            start = max(endhead, endfirsthead, 0) + 1
            footer = self[start:endfoot]
            del self[start:endfoot+1]
        elif endlastfoot > -1:
            start = max(endhead, endfirsthead, 0) + 1
            footer = self[start:endlastfoot]
            del self[start:endlastfoot+1]
  
        # See if this is just a horizontal rule and nothing else
        hline = type(self).hline
        lineonly = 0
        for item in footer:
            if type(item) is hline:
                lineonly = 1 
            elif hasattr(item, 'rstrip'):
                if item.rstrip():
                    lineonly = 0
                    break
            else:
                lineonly = 0
                break

        if lineonly:
            return hline

        return self.getRowsAndCells(footer)

    def getRowsAndCells(self, data=None, cellclass=None):
        """ Group contents of list into rows and cells """
        if data is None:
            data = self[:]
        else:
            data = data[:]

        # Store away the cell and row ending macros
        alignmenttab = type(self).alignmenttab
        cr = type(self).cr
        ArrayRow = type(self).ArrayRow
        Cell = type(self).ArrayDataCell
        if cellclass is not None:
            Cell = cellclass
#       par = type(type(self).context['par'])

        # Create rows and cells
        table = [ArrayRow()]
        table[-1].append(Cell())
        borders = self.getHorizontalBorders(data)
        while data:
            # End of a cell
            if isinstance(data[0], alignmenttab):
                data.pop(0)
                table[-1].append(Cell())

            # End of a row
            elif isinstance(data[0], cr):
                data.pop(0)
                for cell, border in zip(table[-1],borders):
                    self.setBordersOnCell(cell, border)
                table.append(ArrayRow())
                borders = self.getHorizontalBorders(data)
                table[-1].append(Cell())

            # Content of current cell
            else:
                token = data.pop(0)
                current = table[-1][-1]
                # Handle multicolumns
                if type(token) is type(self).multicolumn:
                    current[:] = token
                    # Copy the multicolumn's attributes to the cell
                    current.attributes.update(token.attributes)
                    # Put the same cell in for each spanned cell until
                    # we are finished rendering the table
                    for i in range(token.attributes['colspan']-1):
                        table[-1].append(current)
                else:
                    current.append(token)

        # Put borders on the last row 
        if len(table[-1]) == 1 and len(table[-1][-1]) == 0:
            table.pop()
        if table:
            for cell, border in zip(table[-1],borders):
                self.setBordersOnCell(cell, border, flip=True)

        # Apply colspecs
        if table:
            colspec = None
            if hasattr(self, 'colspec'):
                colspec = self.compileColspec(self.attributes['colspec'])
            if colspec and table:
                for row in table:
                    for i in range(len(row)):
                        if hasattr(row[i], 'colspec'):
                            multcolspec = self.compileColspec(row[i].attributes['colspec'])
                            row[i].style.update(multcolspec[0].style)
                        else:
                            row[i].style.update(colspec[i].style) 

        # Filter out duplicate multicolumn cells, we're done with them.
        for row in table:
            index = 0
            while index < len(row):
                colspan = row[index].attributes.get('colspan', 1)
                if colspan > 1:
                    for i in range(colspan-1):
                        cell = row.pop(index+1)
                        if row[index] is not cell:
                            raise ValueError, 'Error in processing multicolumn'
                index += 1

        # Digest contents of each cell
        for row in table:
            for i in range(len(row)):
               # Strip leading and trailing whitespace, so that
               # we can handle them as empty cells in the renderer
               while row[i]:
                   current = row[i]
                   if hasattr(current[0], 'rstrip'):
                       if not current[0].rstrip():
                           row[i].pop(0)
                       else: break
                   else: break
               while row[i]:
                   current = row[i]
                   if hasattr(current[-1], 'rstrip'):
                       if not current[-1].rstrip():
                           row[i].pop()
                       else: break
                   else: break
#              row[i][:] = paragraphs(tokens2tree(row[i]), par)
               if row[i].attributes.get('colspan',0) == 1:
                   del row[i].attributes['colspan']

        return table

    def setBordersOnCell(self, cell, border, flip=False):
        """
        Set border attributes on the cell

        Required Attributes:
        cell -- the table cell instance
        border -- the border specification
        
        Optional Attributes:
        flip -- boolean indicating whether the top and bottom borders
            should be flipped

        """
        top, bottom = BORDERTOP, BORDERBOTTOM
        if flip:
            top, bottom = BORDERBOTTOM, BORDERTOP
        if border & top:
            cell.style['border-top'] = '1px solid black'
        if border & bottom:
            cell.style['border-bottom'] = '1px solid black'
        if border & BORDERLEFT:
            cell.style['border-left'] = '1px solid black'
        if border & BORDERRIGHT:
            cell.style['border-right'] = '1px solid black'

    def getHorizontalBorders(self, data, location=BORDERTOP):
        """ Get location of horizontal borders """
        borders = [0]*100
        vline = type(self).vline
        cline = type(self).cline
        hline = type(self).hline
        index = 0
        while data:
            current = data[0]
            currenttype = type(current)
            # Set the left border
            if currenttype is vline:
                data.pop(0)
                borders[index] |= BORDERLEFT
            # Set the bottom border all the way across
            elif currenttype is hline:
                data.pop(0)
                for i in range(len(borders)):
                    borders[i] |= location
            # Set the bottom border on specified cells
            elif currenttype is cline:
                data.pop(0)
                begin = current.attributes['span'][0] - 1
                end = current.attributes['span'][1]
                for i in range(begin,end):
                    borders[i] |= location
            # Bypass any whitespace
            elif hasattr(current, 'strip') and not current.strip():
                data.pop(0) 
            else:
                break
        return borders

class tabular(Array):
    args = 'colspec'
    block = True

class longtable(Array):
    args = '[ loc ] colspec'
    block = True

class cr(Command):
    args = '* [ space ]'
