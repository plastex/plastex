#!/usr/bin/env python

import sys
from plasTeX.Base.LaTeX.Arrays import tabular
from plasTeX import Command, Dimen, Count, Glue, dimen, glue, count

class LTleft(Glue): value = glue('1fil')
class LTright(Glue): value = glue('1fil')
class LTpre(Glue): value = glue('1fil')
class LTpost(Glue): value = glue('1fil')
class LTchunksize(Dimen): value = dimen('4in')
class LTchunksize(Count): value = count(20)

class setlongtables(Command): pass

class longtable(tabular):
    args = '[ position:str ] colspec:nox'

    class tabularnewline(Command): pass

    class LongTableEndRow(tabular.EndRow):
        args = None
        macroName = None
        digested = False
        def digest(self, tokens):
            if self.digested:
                return

            tabular.EndRow.digest(self, tokens)

            # Push the instance into the stream a second time.
            # This will be used in longtable.digest() to split out
            # the header and footer chunks.
            tokens.push(self)

            self.digested = True

    class endhead(LongTableEndRow):
        """ End of head section """

    class endfirsthead(LongTableEndRow):
        """ End of first head section """

    class endfoot(LongTableEndRow):
        """ End of footer section """

    class endlastfoot(LongTableEndRow):
        """ End of last footer section """

    class kill(LongTableEndRow):
        """ Throw-away row used for measurement """

    def processRows(self):
        # Strip header and footer chunks from the table
        delims = [x for x in self if isinstance(x, type(self).EndRow)]
        header = footer = None
        for current in delims:
            cache = []
            while 1:
                node = self.pop(0)
                if current is node:
                    if isinstance(current, type(self).endhead):
                        if header is None:
                            header = cache
                    elif isinstance(current, type(self).endfirsthead):
                        header = cache
                    elif isinstance(current, type(self).endfoot):
                        if footer is None:
                            footer = cache
                    elif isinstance(current, type(self).endlastfoot):
                        footer = cache
                    break
                else:
                    cache.append(node)

        # Re-insert only the first header and last footer
        if header is not None:
            header.reverse()
            for item in header:
                for cell in item:
                    cell.isheader = True
                self.insert(0, item)

        if footer is not None:
            for item in footer:
                for cell in item:
                    cell.isheader = True
                self.append(item)
