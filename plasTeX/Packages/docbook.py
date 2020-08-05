# DocBook elements

from plasTeX import Command
from plasTeX.Packages.packageprefix import define_prefixed_exports

exports_to_be_prefixed = ['firstTerm']


def ProcessOptions(options, document):
    define_prefixed_exports(
        options,
        document,
        exports_from_package=exports_to_be_prefixed,
        classes_in_package=globals(),
        prefix_in_package='docbook_',
        default_prefix_in_document='DOCBOOK',
    )


class docbook_firstTerm(Command):
    args = 'self'

# End of file
