# Type theory macros

from plasTeX import Command
from plasTeX.Packages.packageprefix import define_prefixed_exports

exports_to_be_prefixed = [
    'abstraction', 'booleanFalseElement', 'booleanTrueElement', 
    'booleanType', 'codomain', 'coproduct', 'domain', 'element', 
    'emptyType', 'firstInjection', 'firstProjection', 'idFunction',
    'idLoop', 'natural', 'pair', 'pathFamily', 'pathType', 'piType',
    'product', 'same', 'secondInjection', 'secondProjection',
    'sigmaType', 'successor', 'unitType', 'unitTypeElement',
    'universe', 'zeroNatural' 
]


def ProcessOptions(options, document):
    define_prefixed_exports(
        options,
        document,
        exports_from_package=exports_to_be_prefixed,
        classes_in_package=globals(),
        prefix_in_package='typetheory_',
        default_prefix_in_document='TYPETHEORY',
    )


class typetheory_element(Command):
    mathMode = True


class typetheory_same(Command):
    mathMode = True


class typetheory_universe(Command):
    args = '[ grade ]'
    mathMode = True


class typetheory_piType(Command):
    args = '[ index ]'
    mathMode = True


class typetheory_abstraction(Command):
    args = '[ index ]'
    mathMode = True


class typetheory_domain(Command):
    args = 'function'
    mathMode = True


class typetheory_codomain(Command):
    args = 'function'
    mathMode = True


class typetheory_idFunction(Command):
    args = '[ domain ]'
    mathMode = True


class typetheory_sigmaType(Command):
    args = '[ index ]'
    mathMode = True


class typetheory_pair(Command):
    args = 'first_component second_component'
    mathMode = True


class typetheory_product(Command):
    args = 'first_factor second_factor'
    mathMode = True


class typetheory_firstProjection(Command):
    mathMode = True


class typetheory_secondProjection(Command):
    mathMode = True


class typetheory_emptyType(Command):
    mathMode = True


class typetheory_unitType(Command):
    mathMode = True


class typetheory_unitTypeElement(Command):
    mathMode = True


class typetheory_booleanType(Command):
    mathMode = True


class typetheory_booleanTrueElement(Command):
    mathMode = True


class typetheory_booleanFalseElement(Command):
    mathMode = True


class typetheory_coproduct(Command):
    args = 'first_component second_component'
    mathMode = True


class typetheory_firstInjection(Command):
    mathMode = True


class typetheory_secondInjection(Command):
    mathMode = True


class typetheory_natural(Command):
    mathMode = True


class typetheory_zeroNatural(Command):
    mathMode = True


class typetheory_successor(Command):
    mathMode = True


class typetheory_pathFamily(Command):
    mathMode = True
    args = 'base'


class typetheory_pathType(Command):
    mathMode = True
    args = 'start end'


class typetheory_idLoop(Command):
    mathMode = True
    args = 'base'

# End of file
