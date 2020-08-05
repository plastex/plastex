# Package for notes

from plasTeX import Command
from plasTeX.Packages.crossreferences import *
from plasTeX.Packages.generalmathematics import *
from plasTeX.Packages.packageprefix import define_prefixed_exports

exports_to_be_prefixed = [
    'author', 'date', 'makeTitle', 'setTitle', 'shortTitle', 'title'
]


def ProcessOptions(options, document):
    define_prefixed_exports(
        options,
        document,
        exports_from_package=exports_to_be_prefixed,
        classes_in_package=globals(),
        prefix_in_package='basicnotes_',
        default_prefix_in_document='BASICNOTES',
    )


class basicnotes_setTitle(Command):
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


class basicnotes_shortTitle(Command):
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


class basicnotes_makeTitle(Command):
    blockType = True


# End of file
