#!/usr/bin/env python

"""
C.7 Mathematical Formulas (p187)

"""

from Arrays import Array
from plasTeX import Command, Environment, sourceChildren
from plasTeX import DimenCommand, GlueCommand
from plasTeX.Logging import getLogger

#
# C.7.1
#

class MathEnvironment(Environment):
    mathMode = True

    class ThinSpace(Command):
        macroName = '.'

    class NegativeThisSpace(Command):
        macroName = '!'
    
    class MediumSpace(Command):
        macroName = ':'
    
    class ThickSpace(Command):
        macroName = ';'
    
    class ThinSpace_(Command):
        macroName = '/'

# Need \newcommand\({\begin{math}} and \newcommand\){\end{math}}

class math(MathEnvironment): 
    @property
    def source(self): 
        if self.hasChildNodes():
            return '$%s$' % sourceChildren(self)
        return '$'

class displaymath(MathEnvironment):
    blockType = True
    @property
    def source(self):
        if self.hasChildNodes():
            return r'\[ %s \]' % sourceChildren(self)
        if self.macroMode == Command.MODE_END:
            return r'\]'
        return r'\['

class BeginDisplayMath(Command):
    macroName = '['
    def invoke(self, tex):
        o = self.ownerDocument.createElement('displaymath')
        o.macroMode = Command.MODE_BEGIN
        self.ownerDocument.context.push(o)
        return [o]

class EndDisplayMath(Command):
    macroName = ']'
    def invoke(self, tex):
        o = self.ownerDocument.createElement('displaymath')
        o.macroMode = Command.MODE_END
        self.ownerDocument.context.pop(o)
        return [o]

class BeginMath(Command):
    macroName = '('
    def invoke(self, tex):
        o = self.ownerDocument.createElement('math')
        o.macroMode = Command.MODE_BEGIN
        self.ownerDocument.context.push(o)
        return [o]

class EndMath(Command):
    macroName = ')'
    def invoke(self, tex):
        o = self.ownerDocument.createElement('math')
        o.macroMode = Command.MODE_END
        self.ownerDocument.context.pop(o)
        return [o]

class ensuremath(Command):
    args = 'self'

class equation(MathEnvironment):
    blockType = True
    counter = 'equation'

class EqnarrayStar(Array): 
    macroName = 'eqnarray*'
    blockType = True
    mathMode = True

    class lefteqn(Command):
        args = 'self'
        def digest(self, tokens):
            res = Command.digest(self, tokens)
            obj = self.parentNode
            while obj is not None and not isinstance(obj, Array.ArrayCell):
                obj = obj.parentNode
            if obj is not None:
                obj.attributes['colspan'] = 3
                obj.style['text-align'] = 'left'
            return res

    class ArrayCell(Array.ArrayCell):
        @property
        def source(self):
            return '$\\displaystyle %s $' % sourceChildren(self, par=False)

class eqnarray(EqnarrayStar):
    macroName = None
    counter = 'equation'

    class EndRow(Array.EndRow):
        """ End of a row """
        counter = 'equation'
        def invoke(self, tex):
            res = Array.EndRow.invoke(self, tex)
            res[1].ref = self.ref
            self.ownerDocument.context.currentlabel = res[1]
            return res

    def invoke(self, tex):
        res = EqnarrayStar.invoke(self, tex)
        if self.macroMode == self.MODE_END:
            return res
        res[1].ref = self.ref
        return res

class nonumber(Command):

    def invoke(self, tex):
        self.ownerDocument.context.counters['equation'].addtocounter(-1)

    def digest(self, tokens):
        row = self.parentNode
        while not isinstance(row, Array.ArrayRow):
            row = row.parentNode
        row.ref = None

class lefteqn(Command):
    args = 'self'

#
# Style Parameters
#

class jot(DimenCommand):
    value = DimenCommand.new(0)

class mathindent(DimenCommand):
    value = DimenCommand.new(0)

class abovedisplayskip(GlueCommand):
    value = GlueCommand.new(0)

class belowdisplayskip(GlueCommand):
    value = GlueCommand.new(0)

class abovedisplayshortskip(GlueCommand):
    value = GlueCommand.new(0)

class belowdisplayshortskip(GlueCommand):
    value = GlueCommand.new(0)


#
# C.7.2 Common Structures
#

# _ 
# ^
# '

class frac(Command):
    args = 'numer denom'

class sqrt(Command):
    args = '[ n ] self'

class ldots(Command): 
    pass

class cdots(Command):
    pass

class vdots(Command):
    pass

class ddots(Command):
    pass

#
# C.7.3 Mathematical Symbols
#

#
# Table 3.3: Greek Letters
#

class MathSymbol(Command): 
    pass

# Lowercase
class alpha(MathSymbol): pass
class beta(MathSymbol): pass
class gamma(MathSymbol): pass
class delta(MathSymbol): pass
class epsilon(MathSymbol): pass
class varepsilon(MathSymbol): pass
class zeta(MathSymbol): pass
class eta(MathSymbol): pass
class theta(MathSymbol): pass
class vartheta(MathSymbol): pass
class iota(MathSymbol): pass
class kappa(MathSymbol): pass
class GreekLamda(MathSymbol):
    macroName = 'lambda'
class mu(MathSymbol): pass
class nu(MathSymbol): pass
class xi(MathSymbol): pass
class pi(MathSymbol): pass
class varpi(MathSymbol): pass
class rho(MathSymbol): pass
class varrho(MathSymbol): pass
class sigma(MathSymbol): pass
class varsigma(MathSymbol): pass
class tau(MathSymbol): pass
class upsilon(MathSymbol): pass
class phi(MathSymbol): pass
class varphi(MathSymbol): pass
class chi(MathSymbol): pass
class psi(MathSymbol): pass
class omega(MathSymbol): pass

# Uppercase
class Gamma(MathSymbol): pass
class Delta(MathSymbol): pass
class Theta(MathSymbol): pass
class Lambda(MathSymbol): pass
class Xi(MathSymbol): pass
class Pi(MathSymbol): pass
class Sigma(MathSymbol): pass
class Upsilon(MathSymbol): pass
class Phi(MathSymbol): pass
class Psi(MathSymbol): pass
class Omega(MathSymbol): pass


#
# Table 3.4: Binary Operation Symbols
#

class pm(MathSymbol): pass
class mp(MathSymbol): pass
class times(MathSymbol): pass
class div(MathSymbol): pass
class ast(MathSymbol): pass
class star(MathSymbol): pass
class circ(MathSymbol): pass
class bullet(MathSymbol): pass
class cdot(MathSymbol): pass
class cap(MathSymbol): pass
class cup(MathSymbol): pass
class uplus(MathSymbol): pass
class sqcap(MathSymbol): pass
class sqcup(MathSymbol): pass
class vee(MathSymbol): pass
class wedge(MathSymbol): pass
class setminus(MathSymbol): pass
class wr(MathSymbol): pass
class diamond(MathSymbol): pass
class bigtriangleup(MathSymbol): pass
class bigtriangledown(MathSymbol): pass
class triangleleft(MathSymbol): pass
class triangleright(MathSymbol): pass
class lhd(MathSymbol): pass
class rhd(MathSymbol): pass
class unlhd(MathSymbol): pass
class unrhd(MathSymbol): pass
class oplus(MathSymbol): pass
class ominus(MathSymbol): pass
class otimes(MathSymbol): pass
class oslash(MathSymbol): pass
class odot(MathSymbol): pass
class bigcirc(MathSymbol): pass
class dagger(MathSymbol): pass
class ddagger(MathSymbol): pass
class amalg(MathSymbol): pass

#
# Table 3.5: Relation Symbols
#

class Not(MathSymbol):
    macroName = 'not'
    args = 'symbol'
class leq(MathSymbol): pass
class le(MathSymbol): pass
class prec(MathSymbol): pass
class preceq(MathSymbol): pass
class ll(MathSymbol): pass
class subset(MathSymbol): pass
class subseteq(MathSymbol): pass
class sqsubseteq(MathSymbol): pass
class In(MathSymbol):
    macroName = 'in'
class vdash(MathSymbol): pass
class geq(MathSymbol): pass
class ge(MathSymbol): pass
class succ(MathSymbol): pass
class succeq(MathSymbol): pass
class gg(MathSymbol): pass
class supset(MathSymbol): pass
class supseteq(MathSymbol): pass
class sqsupset(MathSymbol): pass
class sqsupseteq(MathSymbol): pass
class ni(MathSymbol): pass
class dashv(MathSymbol): pass
class equiv(MathSymbol): pass
class sim(MathSymbol): pass
class simeq(MathSymbol): pass
class asymp(MathSymbol): pass
class approx(MathSymbol): pass
class cong(MathSymbol): pass
class neq(MathSymbol): pass
class ne(MathSymbol): pass
class doteq(MathSymbol): pass
class notin(MathSymbol): pass
class models(MathSymbol): pass
class perp(MathSymbol): pass
class mid(MathSymbol): pass
class parallel(MathSymbol): pass
class bowtie(MathSymbol): pass
class Join(MathSymbol): pass
class smile(MathSymbol): pass
class frown(MathSymbol): pass
class propto(MathSymbol): pass

#
# Table 3.6: Arrow Symbols
#

class leftarrow(MathSymbol): pass
class Leftarrow(MathSymbol): pass
class rightarrow(MathSymbol): pass
class Rightarrow(MathSymbol): pass
class leftrightarrow(MathSymbol): pass
class Leftrightarrow(MathSymbol): pass
class mapsto(MathSymbol): pass
class hookleftarrow(MathSymbol): pass
class leftharpoonup(MathSymbol): pass
class leftharpoondown(MathSymbol): pass
class rightleftharpoons(MathSymbol): pass
class longleftarrow(MathSymbol): pass
class Longleftarrow(MathSymbol): pass
class longrightarrow(MathSymbol): pass
class Longrightarrow(MathSymbol): pass
class longleftrightarrow(MathSymbol): pass
class Longleftrightarrow(MathSymbol): pass
class longmapsto(MathSymbol): pass
class hookrightarrow(MathSymbol): pass
class rightharpoonup(MathSymbol): pass
class rightharpoondown(MathSymbol): pass
class leadsto(MathSymbol): pass
class uparrow(MathSymbol): pass
class Uparrow(MathSymbol): pass
class downarrow(MathSymbol): pass
class Downarrow(MathSymbol): pass
class updownarrow(MathSymbol): pass
class Updownarrow(MathSymbol): pass
class nearrow(MathSymbol): pass
class searrow(MathSymbol): pass
class swarrow(MathSymbol): pass
class nwarrow(MathSymbol): pass

#
# Table 3.7: Miscellaneous Symbols
#

class aleph(MathSymbol): pass
class hbar(MathSymbol): pass
class imath(MathSymbol): pass
class jmath(MathSymbol): pass
class ell(MathSymbol): pass
class wp(MathSymbol): pass
class Re(MathSymbol): pass
class Im(MathSymbol): pass
class mho(MathSymbol): pass
class prime(MathSymbol): pass
class emptyset(MathSymbol): pass
class nabla(MathSymbol): pass
class surd(MathSymbol): pass
class top(MathSymbol): pass
class bot(MathSymbol): pass
class VerticalBar(MathSymbol):
    macroName = '|'
class forall(MathSymbol): pass
class exists(MathSymbol): pass
class neg(MathSymbol): pass
class flat(MathSymbol): pass
class natural(MathSymbol): pass
class sharp(MathSymbol): pass
class backslash(MathSymbol): pass
class partial(MathSymbol): pass
class infty(MathSymbol): pass
class Box(MathSymbol): pass
class Diamond(MathSymbol): pass
class triangle(MathSymbol): pass
class clubsuit(MathSymbol): pass
class diamondsuit(MathSymbol): pass
class heartsuit(MathSymbol): pass
class spadesuit(MathSymbol): pass

#
# Table 3.8: Variable-sized Symbols
#

class sum(MathSymbol): pass
class prod(MathSymbol): pass
class coprod(MathSymbol): pass
class int(MathSymbol): pass
class oint(MathSymbol): pass
class bigcap(MathSymbol): pass
class bigcup(MathSymbol): pass
class bigsqcup(MathSymbol): pass
class bigvee(MathSymbol): pass
class bigwedge(MathSymbol): pass
class bigodot(MathSymbol): pass
class bigotimes(MathSymbol): pass
class bigoplus(MathSymbol): pass
class biguplus(MathSymbol): pass

#
# Table 3.9: Log-like Functions
#

class Logarithm(MathSymbol):
    macroName = 'log'
class bmod(MathSymbol): pass
class pmod(MathSymbol):
    args = 'self'
class arccos(MathSymbol): pass
class arcsin(MathSymbol): pass
class arctan(MathSymbol): pass
class arg(MathSymbol): pass
class cos(MathSymbol): pass
class cosh(MathSymbol): pass
class cot(MathSymbol): pass
class coth(MathSymbol): pass
class csc(MathSymbol): pass
class deg(MathSymbol): pass
class det(MathSymbol): pass
class dim(MathSymbol): pass
class exp(MathSymbol): pass
class gcd(MathSymbol): pass
class hom(MathSymbol): pass
class inf(MathSymbol): pass
class ker(MathSymbol): pass
class lg(MathSymbol): pass
class lim(MathSymbol): pass
class liminf(MathSymbol): pass
class limsup(MathSymbol): pass
class ln(MathSymbol): pass
class log(MathSymbol): pass
class max(MathSymbol): pass
class min(MathSymbol): pass
class Pr(MathSymbol): pass
class sec(MathSymbol): pass
class sin(MathSymbol): pass
class sinh(MathSymbol): pass
class sup(MathSymbol): pass
class tan(MathSymbol): pass
class tanh(MathSymbol): pass


#
# C.7.4 Arrays (see Arrays.py)
#

#
# C.7.5 Delimiters
#

class left(Command): 
    args = 'delim'

class right(Command):
    args = 'delim'

# Table 3.10: Delimiters and TeXbook (p359)

class Delimiter(Command):
    pass

class langle(Delimiter): pass
class rangle(Delimiter): pass
class lbrace(Delimiter): pass
class rbrace(Delimiter): pass
class lceil(Delimiter): pass
class rceil(Delimiter): pass
class lfloor(Delimiter): pass
class rfloor(Delimiter): pass
class lgroup(Delimiter): pass
class rgroup(Delimiter): pass
class lmoustache(Delimiter): pass
class rmoustache(Delimiter): pass
class uparrow(Delimiter): pass
class Uparrow(Delimiter): pass
class downarrow(Delimiter): pass
class Downarrow(Delimiter): pass
class updownarrow(Delimiter): pass
class Updownarrow(Delimiter): pass
class arrowvert(Delimiter): pass
class Arrowvert(Delimiter): pass
class vert(Delimiter): pass
class Vert(Delimiter): pass
class backslash(Delimiter): pass
class bracevert(Delimiter): pass

class bigl(Delimiter): pass
class bigm(Delimiter): pass
class bigr(Delimiter): pass
class Bigl(Delimiter): pass
class Bigm(Delimiter): pass
class Bigr(Delimiter): pass
class biggl(Delimiter): pass
class biggr(Delimiter): pass
class Biggl(Delimiter): pass
class Biggr(Delimiter): pass
class biggm(Delimiter): pass
class Biggm(Delimiter): pass
class Big(Delimiter):
    args = 'char'
class bigg(Delimiter):
    args = 'char'
class Bigg(Delimiter):
    args = 'char'

class choose(Command):
    pass

class brack(Command):
    pass

class brace(Command):
    pass

class sqrt(Command):
    pass

#
# C.7.6 Putting One Thing Above Another
#

class overline(Command):
    args = 'self'

class underline(Command):
    args = 'self'

class overbrace(Command):
    args = 'self'

class underbrace(Command):
    args = 'self'

# Accents

class MathAccent(Command):
    args = 'self'

class hat(MathAccent): pass
class check(MathAccent): pass
class breve(MathAccent): pass
class acute(MathAccent): pass
class grave(MathAccent): pass
class tilde(MathAccent): pass
class bar(MathAccent): pass
class vec(MathAccent): pass
class dot(MathAccent): pass
class ddot(MathAccent): pass

class widehat(MathAccent): pass
class widetilde(MathAccent): pass
class imath(MathAccent): pass
class jmath(MathAccent): pass
class stackrel(MathAccent):
    args = 'top bottom'

#
# C.7.7 Spacing
# 

# These are nested inside the MathEnvironemnt


#
# C.7.8 Changing Style
#

# Type Style

class mathrm(Command):
    args = 'self'

class mathit(Command):
    args = 'self'

class mathbf(Command):
    args = 'self'

class mathsf(Command):
    args = 'self'

class mathtt(Command):
    args = 'self'

class mathcal(Command):
    args = 'self'

class boldmath(Command):
    pass

class unboldmath(Command):
    pass

# Math Style

class displaystyle(Command):
    pass

class textstyle(Command):
    pass

class scriptstyle(Command):
    pass

class scriptscriptstyle(Command):
    pass



