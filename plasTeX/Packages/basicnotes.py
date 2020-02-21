# Package for notes

from plasTeX import Command
from plasTeX.Packages.crossreferences import *
from plasTeX.Packages.generalmathematics import *

package_prefix_exports = [
    'author', 'date', 'maketitle', 'settitle', 'title', 'titleabbrev'
]


class basicnotes_settitle(Command):
    args = 'self'

    def invoke(self, tex):
        super().invoke(tex)
        self.ownerDocument.userdata['set-title'] = self


class basicnotes_title(Command):
    args = '[ toc ] self'

    def invoke(self, tex):
        Command.invoke(self, tex)
        if 'title' not in list(self.ownerDocument.userdata.keys()):
            self.ownerDocument.userdata['title'] = self


class basicnotes_titleabbrev(Command):
    pass


class basicnotes_author(Command):
    args = 'self'

    def invoke(self, tex):
        super().invoke(tex)
        userdata = self.ownerDocument.userdata
        if userdata.get('author') is None:
            userdata['author'] = []
        userdata['author'].append(self)


class basicnotes_date(Command):
    args = 'self'

    def invoke(self, tex):
        super().invoke(tex)
        self.ownerDocument.userdata['date'] = self


class basicnotes_maketitle(Command):
    blockType = True


# End of file
