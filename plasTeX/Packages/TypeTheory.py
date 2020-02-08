from plasTeX import Command


class TTelement(Command):
    mathMode = True


class TTsame(Command):
    mathMode = True


class TTuniverse(Command):
    args = '[ grade ]'
    mathMode = True


class TTpitype(Command):
    args = '[ index ]'
    mathMode = True


class TTabstraction(Command):
    args = '[ index ]'
    mathMode = True


class TTdomain(Command):
    args = 'function'
    mathMode = True


class TTcodomain(Command):
    args = 'function'
    mathMode = True


class TTidfunction(Command):
    args = '[ domain ]'
    mathMode = True


class TTsigmatype(Command):
    args = '[ index ]'
    mathMode = True


class TTpair(Command):
    args = 'first_component second_component'
    mathMode = True


class TTproduct(Command):
    args = 'first_factor second_factor'
    mathMode = True


class TTfirstprojection(Command):
    mathMode = True


class TTsecondprojection(Command):
    mathMode = True


class TTemptytype(Command):
    mathMode = True


class TTunittype(Command):
    mathMode = True


class TTunittypeelement(Command):
    mathMode = True


class TTbooleantype(Command):
    mathMode = True


class TTbooleantrueelement(Command):
    mathMode = True


class TTbooleanfalseelement(Command):
    mathMode = True


class TTcoproduct(Command):
    args = 'first_component second_component'
    mathMode = True


class TTfirstinjection(Command):
    mathMode = True


class TTsecondinjection(Command):
    mathMode = True


class TTnatural(Command):
    mathMode = True


class TTbooleantype(Command):
    mathMode = True


class TTzeronatural(Command):
    mathMode = True


class TTsuccessor(Command):
    mathMode = True


class TTpathfamily(Command):
    mathMode = True
    args = 'base'


class TTpathtype(Command):
    mathMode = True
    args = 'start end'


class TTidloop(Command):
    mathMode = True
    args = 'base'
