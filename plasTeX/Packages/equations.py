from plasTeX.Base.LaTeX.Math import MathEnvironment


class EquationStar(MathEnvironment):
    macroName = 'equation*'
    blockType = False
