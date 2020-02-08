from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Math import MathEnvironment


class EquationStar(MathEnvironment):
    macroName = 'equation*'
    blockType = False


class dotsc(Command):
    mathMode = True
    pass


class LowerCaseLambda(Command):
    macroName = 'lambda'
    mathMode = True


class LowerCaseEta(Command):
    macroName = 'eta'
    mathMode = True


class LowerCaseSigma(Command):
    macroName = 'sigma'
    mathMode = True


class circ(Command):
    mathMode = True


class LowerCasePhi(Command):
    macroName = 'phi'
    mathMode = True


class LowerCaseTau(Command):
    macroName = 'tau'
    mathMode = True


class LowerCasePsi(Command):
    macroName = 'psi'
    mathMode = True


class LowerCaseEpsilon(Command):
    macroName = 'epsilon'
    mathMode = True
