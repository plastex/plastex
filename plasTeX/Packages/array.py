#!/usr/bin/env python

import new
from plasTeX.Utils import *
from plasTeX import Macro, Environment, Command

class ColumnType(Macro):

    columnAttributes = {}
    columnTypes = {}

    def __init__(self, *args, **kwargs):
        Macro.__init__(self, *args, **kwargs)
        self.style.update(self.columnAttributes)
        
    def new(cls, name, attributes, args='', before=[], after=[]):
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
             'before':before, 'after':after})
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

    class alignmenttab(Command):
        """ Cell delimiter """
        def invoke(self, tex):
            # Pop and push a new context for each cell, this keeps
            # any formatting changes from the previous cell from
            # leaking over into the next cell
            tex.context.pop()
            tex.context.push()
            # Add a phantom cell to absorb the appropriate tokens
            return [self, Array.ArrayCell()]

        def source(self):
            return '&'
        source = property(source)

    class endrow(Command):
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

    class cline(Command):
        """ Partial horizontal line """
        args = 'span:str'
        def invoke(self, tex):
            self.parse(tex)
            attrs = self.attributes
            attrs['span'] = [int(x) for x in attrs['span'].split('-')]
            if len(attrs['span']) == 1:
                attrs['span'] *= 2

    class hline(Command):
        """ Full horizontal line """

    class vline(Command):
        """ Vertical line """

    class ArrayRow(Macro):
        """ Table row class """
        endtoken = None
        def digest(self, tokens):
            self.endtoken = self.digestUntil(tokens, Array.endrow)
            if self.endtoken is not None:
                tokens.next()
                self.endtoken.digest(tokens)
        def source(self):
            if self.endtoken is not None:
                return sourcechildren(self) + self.endtoken.source
            return sourcechildren(self)
        source = property(source)

    class ArrayCell(Macro):
        """ Table cell class """
        endtoken = None
        colspan = 1
        rowspan = 1
        def digest(self, tokens):
            self.endtoken = self.digestUntil(tokens, (Array.alignmenttab, 
                                                      Array.endrow))
            if isinstance(self.endtoken, Array.alignmenttab):
                tokens.next()
                self.endtoken.digest(tokens)
            else:
                self.endtoken = None
        def source(self):
            if self.endtoken is not None:
                return sourcechildren(self) + self.endtoken.source
            return sourcechildren(self)
        source = property(source)

    class multicolumn(Command):
        """ Column spanning cell """
        args = 'colspan:int colspec text'

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
            self.compileColspec(self.attributes['colspec'])

        tex.context.push() # Beginning of cell
        # Add a phantom row and cell to absorb the appropriate tokens
        return [self, Array.ArrayRow(), Array.ArrayCell()]

    def compileColspec(self, colspec):
        """ Compile colspec into an object """
        colspec = [x for x in colspec if x.nodeType == x.ELEMENT_NODE or x.catcode != x.CC_SPACE]

        # Strip any left borders, all other borders will be on the right
        leftborder = False
        while colspec and colspec[0] == '|':
            leftborder = True 
            colspec.pop(0)

        output = []
        for item in iter(colspec):
            if item.nodeType == item.ELEMENT_NODE: 
                continue

            if item == '|':
                output[-1].style['border-right'] = '1px solid black'
                continue

            if item in '<>':
                continue

            output.append(ColumnType.columnTypes.get(item, ColumnType)())

        if leftborder:
            output[0].style['border-left'] = '1px solid black'
             
        return output


class tabular(Array):
    args = 'colspec'

class cr(Command):
    macroName = '\\'
    args = '* [ space ]'

class array(Array):
    args = 'colspec'
