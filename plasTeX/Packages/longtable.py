#!/usr/bin/env python

from Context import Context
from array import tabular
from plasTeX import Environment, Command, Dimen, Counter, Glue

context = Context()
context.newskip('LTleft', 0)
context.newskip('LTright', 0)
context.newskip('LTpre', 0)
context.newskip('LTpost', 0)
context.newdimen('LTchunksize', '4in')
context.newcounter('LTchunksize', 20)

class setlongtables(Command): pass

class longtable(tabular):
    args = '[ position:str ] colspec'

    class tabularnewline(Command): pass

    class longtableendrow(tabular.endrow):
        args = None
        macroName = None
        digested = False
        def digest(self, tokens):
            if self.digested:
                return

            tabular.endrow.digest(self, tokens)

            # Push the instance into the stream a second time.
            # This will be used in longtable.digest() to split out
            # the header and footer chunks.
            tokens.push(self)

            self.digested = True

    class endhead(longtableendrow):
        """ End of head section """

    class endfirsthead(longtableendrow):
        """ End of first head section """

    class endfoot(longtableendrow):
        """ End of footer section """

    class endlastfoot(longtableendrow):
        """ End of last footer section """

    class kill(longtableendrow):
        """ Throw-away row used for measurement """

    def digest(self, tokens):
        tabular.digest(self, tokens)

        if self.macroMode == self.MODE_END:
            return

        # Strip header and footer chunks from the table
        headers = [x for x in self if isinstance(x, type(self).endrow)]
        header = footer = None
        for current in headers:
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
            for item in header:
                self.insert(0, item)

        if footer is not None:
            for item in footer:
                self.append(item)
