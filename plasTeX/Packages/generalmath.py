# Mathematical symbols from maths-symbols.tex

from plasTeX import Command
from plasTeX.Base.LaTeX.Math import MathEnvironment


class EquationStar(MathEnvironment):
    macroName = 'equation*'
    blockType = False


mathematical_symbols_with_no_arguments = []
mathematical_symbols_with_one_argument = []


greek_letters = [
    'alpha', 'theta', 'tau', 'beta', 'vartheta', 'pi', 'upsilon',
    'gamma', 'iota', 'varpi', 'phi', 'delta', 'kappa', 'rho',
    'varphi', 'epsilon', 'lambda', 'varrho', 'chi', 'varepsilon',
    'mu', 'sigma', 'psi', 'zeta', 'nu', 'varsigma', 'omega', 'eta',
    'xi', 'Gamma', 'Lambda', 'Sigma', 'Psi', 'Delta', 'Xi',
    'Upsilon', 'Omega', 'Theta', 'Pi', 'Phi'
]

mathematical_symbols_with_no_arguments.extend(greek_letters)


binary_operation_symbols = [
    'pm', 'cap', 'diamond', 'oplus', 'mp', 'cup', 'bigtriangleup',
    'ominus', 'times', 'uplus', 'bigtriangledown', 'otimes', 'div',
    'sqcap', 'triangleleft', 'oslash', 'ast', 'sqcup',
    'triangleright', 'odot', 'star', 'vee', 'lhd', 'bigcirc', 'circ',
    'wedge', 'rhd', 'dagger', 'bullet', 'setminus', 'unlhd',
    'ddagger', 'cdot', 'wr', 'unrhd', 'amalg'
]

mathematical_symbols_with_no_arguments.extend(
    binary_operation_symbols
)


relation_symbols = [
    'leq', 'geq', 'equiv', 'models', 'prec', 'succ',
    'sim', 'perp', 'preceq', 'succeq', 'simeq', 'mid', 'll', 'gg',
    'asymp', 'parallel', 'subset', 'supset', 'approx', 'bowtie',
    'subseteq', 'supseteq', 'cong', 'Join', 'sqsubset', 'sqsupset',
    'neq', 'smile', 'sqsubseteq', 'sqsupseteq', 'doteq', 'frown',
    'in', 'ni', 'propto', 'vdash', 'dashv'
]

mathematical_symbols_with_no_arguments.extend(
    binary_operation_symbols
)


punctuation_symbols = ['colon', 'ldotp', 'cdotp']

mathematical_symbols_with_no_arguments.extend(punctuation_symbols)


arrow_symbols = [
    'leftarrow', 'longleftarrow', 'uparrow', 'Leftarrow',
    'Longleftarrow', 'Uparrow', 'rightarrow', 'longrightarrow',
    'downarrow', 'Rightarrow', 'Longrightarrow', 'Downarrow',
    'leftrightarrow', 'longleftrightarrow', 'updownarrow',
    'Leftrightarrow', 'Longleftrightarrow', 'Updownarrow',
    'mapsto', 'longmapsto', 'nearrow', 'hookleftarrow',
    'hookrightarrow', 'searrow', 'leftharpoonup', 'rightharpoonup',
    'swarrow', 'leftharpoondown', 'rightharpoondown', 'nwarrow',
    'rightleftharpoons', 'leadsto'
]

mathematical_symbols_with_no_arguments.extend(arrow_symbols)


miscellaneous_symbols = [
    'ldots', 'cdots', 'vdots', 'ddots', 'aleph',
    'prime', 'forall', 'infty', 'hbar', 'emptyset', 'exists', 'Box',
    'imath', 'nabla', 'neg', 'Diamond', 'jmath', 'surd', 'flat',
    'triangle', 'ell', 'top', 'natural', 'clubsuit', 'wp', 'bot',
    'sharp', 'diamondsuit', 'Re', 'backslash', 'heartsuit', 'Im',
    'angle', 'partial', 'spadesuit', 'mho', 'dotsc', 'dotsb', 'dotsm',
    'dotsi', 'dotso'
]

mathematical_symbols_with_no_arguments.extend(miscellaneous_symbols)


variable_sized_symbols = [
    'sum', 'bigcap', 'bigodot', 'prod',
    'bigcup', 'bigotimes', 'coprod', 'bigsqcup', 'bigoplus', 'int',
    'bigvee', 'biguplus', 'oint', 'bigwedge'
]

mathematical_symbols_with_no_arguments.extend(variable_sized_symbols)


log_like_symbols = [
    'arccos', 'cos', 'csc', 'exp', 'ker', 'limsup',
    'min', 'sinh', 'arcsin', 'cosh', 'deg', 'gcd', 'lg', 'ln', 'Pr',
    'sup', 'arctan', 'cot', 'det', 'hom', 'lim', 'log', 'sec', 'tan',
    'arg', 'coth', 'dim', 'inf', 'liminf', 'max', 'sin', 'tanh'
]

mathematical_symbols_with_no_arguments.extend(log_like_symbols)


delimiters = [
    'uparrow', 'Uparrow', 'downarrow', 'Downarrow', 'updownarrow',
    'Updownarrow', 'lfloor', 'rfloor', 'lceil', 'rceil', 'langle',
    'rangle', 'backslash'
]

mathematical_symbols_with_no_arguments.extend(delimiters)


large_delimiters = [
    'rmoustache', 'lmoustache', 'rgroup', 'lgroup', 'arrowvert',
    'Arrowvert', 'bracevert'
]

mathematical_symbols_with_no_arguments.extend(large_delimiters)


math_mode_accents = [
    'hat', 'acute', 'bar', 'dot', 'breve', 'check', 'grave', 'vec',
    'ddot', 'tilde'
]

mathematical_symbols_with_one_argument.extend(math_mode_accents)


some_other_constructions = [
    'widetilde', 'widehat', 'overleftarrow', 'overrightarrow',
    'overline', 'underline', 'overbrace', 'underbrace'
]

mathematical_symbols_with_one_argument.extend(
    some_other_constructions
)


class Sqrt(Command):
    macroName = 'sqrt'
    args = '[degree] operand'
    mathMode = True


class Frac(Command):
    macroName = 'frac'
    args = 'numerator denominator'
    mathMode = True


ams_delimiters = ['ulcorner', 'urcorner', 'llcorner', 'lrcorner']

mathematical_symbols_with_no_arguments.extend(ams_delimiters)


ams_arrows = [
    'dashrightarrow', 'dashleftarrow', 'leftleftarrows',
    'leftrightarrows', 'Lleftarrow', 'twoheadleftarrow',
    'leftarrowtail', 'looparrowleft', 'leftrightharpoons',
    'curvearrowleft', 'circlearrowleft', 'Lsh', 'upuparrows',
    'upharpoonleft', 'downharpoonleft', 'multimap',
    'leftrightsquigarrow', 'rightrightarrows', 'rightleftarrows',
    'rightrightarrows', 'rightleftarrows', 'twoheadrightarrow',
    'rightarrowtail', 'looparrowright', 'rightleftharpoons',
    'curvearrowright', 'circlearrowright', 'Rsh', 'downdownarrows',
    'upharpoonright', 'downharpoonright', 'rightsquigarrow'
]

mathematical_symbols_with_no_arguments.extend(ams_arrows)


ams_negated_arrows = [
    'nleftarrow', 'nrightarrow', 'nLeftarrow', 'nRightarrow',
    'nleftrightarrow', 'nLeftrightarrow'
]

mathematical_symbols_with_no_arguments.extend(ams_negated_arrows)


ams_greek = ['digamma', 'varkappa']

mathematical_symbols_with_no_arguments.extend(ams_greek)


ams_hebrew = ['beth', 'daleth', 'gimel']

mathematical_symbols_with_no_arguments.extend(ams_hebrew)


ams_miscellaneous = [
    'hbar', 'hslash', 'vartriangle', 'triangledown', 'square',
    'lozenge', 'circledS', 'angle', 'measuredangle', 'nexists', 'mho',
    'Finv', 'Game', 'Bbbk', 'backprime', 'varnothing',
    'blacktriangle', 'blacktriangledown', 'blacksquare',
    'blacklozenge', 'bigstar', 'sphericalangle', 'complement', 'eth',
    'diagup', 'diagdown'
]

mathematical_symbols_with_no_arguments.extend(ams_miscellaneous)


ams_binary_operators = [
    'dotplus', 'smallsetminus', 'Cap', 'Cup', 'barwedge', 'veebar',
    'doublebarwedge', 'boxminus', 'boxtimes', 'boxdot', 'boxplus',
    'divideontimes', 'ltimes', 'rtimes', 'leftthreetimes',
    'rightthreetimes', 'curlywedge', 'curlyvee', 'circleddash',
    'circledast', 'circledcirc', 'centerdot', 'intercal'
]

mathematical_symbols_with_no_arguments.extend(ams_binary_operators)


ams_binary_relations = [
    'leqq', 'leqslant', 'eqslantless', 'lesssim', 'lessapprox',
    'approxeq', 'lessdot', 'lll', 'lessgtr', 'lesseqgtr',
    'lesseqqgtr', 'doteqdot', 'risingdotseq', 'fallingdotseq',
    'backsim', 'backsimeq', 'subseteqq', 'Subset', 'sqsubset',
    'preccurlyeq', 'curlyeqprec', 'precsim', 'precapprox',
    'vartriangleleft', 'trianglelefteq', 'vDash', 'Vvdash',
    'smallsmile', 'smallfrown', 'bumpeq', 'Bumpeq', 'geqq',
    'geqslant', 'eqslantgtr', 'gtrsim', 'gtrapprox', 'gtrdot', 'ggg',
    'gtrless', 'gtreqless', 'gtreqqless', 'eqcirc', 'circeq',
    'triangleq', 'thicksim', 'thickapprox', 'supseteqq', 'Supset',
    'sqsupset', 'succcurlyeq', 'curlyeqsucc', 'succsim', 'succapprox',
    'vartriangleright', 'trianglerighteq', 'Vdash', 'shortmid',
    'shortparallel', 'between', 'pitchfork', 'varpropto',
    'blacktriangleleft', 'therefore', 'backepsilon',
    'blacktriangleright', 'because'
]

mathematical_symbols_with_no_arguments.extend(ams_binary_relations)


ams_negated_binary_relations = [
    'nless', 'nleq', 'nleqslant', 'nleqq', 'lneq', 'lneqq',
    'lvertneqq', 'lnsim', 'lnapprox', 'nprec', 'npreceq', 'precnsim',
    'precnapprox', 'nsim', 'nshortmid', 'nmid', 'nvdash', 'nvDash',
    'ntriangleleft', 'ntrianglelefteq', 'nsubseteq', 'subsetneq',
    'varsubsetneq', 'subsetneqq', 'varsubsetneqq', 'ngtr', 'ngeq',
    'ngeqslant', 'ngeqq', 'gneq', 'gneqq', 'gvertneqq', 'gnsim',
    'gnapprox', 'nsucc', 'nsucceq', 'nsucceq', 'succnsim',
    'succnapprox', 'ncong', 'nshortparallel', 'nparallel', 'nvDash',
    'nVDash', 'ntriangleright', 'ntrianglerighteq', 'nsupseteq',
    'nsupseteqq', 'supsetneq', 'varsupsetneq', 'supsetneqq',
    'varsupsetneqq'
]

mathematical_symbols_with_no_arguments.extend(
    ams_negated_binary_relations
)


math_alphabets = [
    'mathrm', 'mathit', 'mathnormal', 'mathcal', 'mathscr',
    'mathfrak', 'mathbb'
]

mathematical_symbols_with_one_argument.extend(math_alphabets)


def define_class_mathematical_symbol_with_no_arguments(symbol_name):
    class_name = 'MathematicalSymbolWithNoArguments_' + symbol_name
    globals()[class_name] = type(
        class_name,
        (Command,),
        {'macroName': symbol_name, 'mathMode': True}
    )


for symbol in mathematical_symbols_with_no_arguments:
    define_class_mathematical_symbol_with_no_arguments(symbol)


def define_class_mathematical_symbol_with_one_argument(symbol_name):
    class_name = 'MathematicalSymbolWithOneArgument_' + symbol_name
    globals()[class_name] = type(
        class_name,
        (Command,),
        {
            'macroName': symbol_name,
            'args': 'argument',
            'mathMode': True
        }
    )


for symbol in mathematical_symbols_with_one_argument:
    define_class_mathematical_symbol_with_one_argument(symbol)

# End of file
