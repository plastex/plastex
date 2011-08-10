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

# These space commands are only documented as being available in math mode,
# but it was requested to have them be in the global namespace.

class ThinSpace(Command):
    macroName = '.'
    unicode = u'\u2009'

class NegativeThinSpace(Command):
    macroName = '!'

class MediumSpace(Command):
    macroName = ':'
    unicode = u'\u8196'

class ThickSpace(Command):
    macroName = ';'
    unicode = u'\u8194'

class ThinSpace_(Command):
    macroName = '/'
    unicode = u'\u2009'

class MathEnvironment(Environment):
    mathMode = True

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

class notag(nonumber):
    pass

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
    unicode = u'\u2026'

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
class alpha(MathSymbol): unicode = unichr(945)
class beta(MathSymbol): unicode = unichr(946)
class gamma(MathSymbol): unicode = unichr(947)
class delta(MathSymbol): unicode = unichr(948)
class epsilon(MathSymbol): unicode = unichr(949)
class varepsilon(MathSymbol): unicode = unichr(949)
class zeta(MathSymbol): unicode = unichr(950)
class eta(MathSymbol): unicode = unichr(951)
class theta(MathSymbol): unicode = unichr(952)
class vartheta(MathSymbol): unicode = unichr(977)
class iota(MathSymbol): unicode = unichr(953)
class kappa(MathSymbol): unicode = unichr(954)
class GreekLamda(MathSymbol):
    macroName = 'lambda'
    unicode = unichr(955)
class mu(MathSymbol): unicode = unichr(956)
class nu(MathSymbol): unicode = unichr(957)
class xi(MathSymbol): unicode = unichr(958)
class pi(MathSymbol): unicode = unichr(960)
class varpi(MathSymbol): unicode = unichr(982)
class rho(MathSymbol): unicode = unichr(961)
class varrho(MathSymbol): unicode = unichr(1009)
class sigma(MathSymbol): unicode = unichr(963)
class varsigma(MathSymbol): unicode = unichr(962)
class tau(MathSymbol): unicode = unichr(964)
class upsilon(MathSymbol): unicode = unichr(965)
class phi(MathSymbol): unicode = unichr(966)
class varphi(MathSymbol): unicode = unichr(981)
class chi(MathSymbol): unicode = unichr(967)
class psi(MathSymbol): unicode = unichr(968)
class omega(MathSymbol): unicode = unichr(969)

# Uppercase
class Gamma(MathSymbol): unicode = unichr(915)
class Delta(MathSymbol): unicode = unichr(916)
class Theta(MathSymbol): unicode = unichr(920)
class Lambda(MathSymbol): unicode = unichr(923)
class Xi(MathSymbol): unicode = unichr(926)
class Pi(MathSymbol): unicode = unichr(928)
class Sigma(MathSymbol): unicode = unichr(931)
class Upsilon(MathSymbol): unicode = unichr(978)
class Phi(MathSymbol): unicode = unichr(934)
class Psi(MathSymbol): unicode = unichr(936)
class Omega(MathSymbol): unicode = unichr(8486)


#
# Table 3.4: Binary Operation Symbols
#

class pm(MathSymbol): unicode = unichr(177)
class mp(MathSymbol): unicode = unichr(8723)
class times(MathSymbol): unicode = unichr(215)
class div(MathSymbol): unicode = unichr(247)
class ast(MathSymbol): unicode = unichr(42)
class star(MathSymbol): unicode = unichr(8902)
class circ(MathSymbol): unicode = unichr(9675)
class bullet(MathSymbol): unicode = unichr(8226)
class cdot(MathSymbol): unicode = unichr(183)
class cap(MathSymbol): unicode = unichr(8745)
class cup(MathSymbol): unicode = unichr(8746)
class uplus(MathSymbol): unicode = unichr(8846)
class sqcap(MathSymbol): unicode = unichr(8851)
class sqcup(MathSymbol): unicode = unichr(8852)
class vee(MathSymbol): unicode = unichr(8744)
class wedge(MathSymbol): unicode = unichr(8743)
class setminus(MathSymbol): unicode = unichr(8726)
class wr(MathSymbol): unicode = unichr(8768)
class diamond(MathSymbol): unicode = unichr(8900)
class bigtriangleup(MathSymbol): unicode = unichr(9651)
class bigtriangledown(MathSymbol): unicode = unichr(9661)
class triangleleft(MathSymbol): unicode = unichr(9667)
class triangleright(MathSymbol): unicode = unichr(9657)
class lhd(MathSymbol): pass
class rhd(MathSymbol): pass
class unlhd(MathSymbol): pass
class unrhd(MathSymbol): pass
class oplus(MathSymbol): unicode = unichr(8853)
class ominus(MathSymbol): unicode = unichr(8854)
class otimes(MathSymbol): unicode = unichr(8855)
class oslash(MathSymbol): unicode = unichr(8856)
class odot(MathSymbol): unicode = unichr(8857)
class bigcirc(MathSymbol): unicode = unichr(9711)
class dagger(MathSymbol): unicode = unichr(8224)
class ddagger(MathSymbol): unicode = unichr(8225)
class amalg(MathSymbol): unicode = unichr(8720)

#
# Table 3.5: Relation Symbols
#

class Not(MathSymbol):
    macroName = 'not'
    args = 'symbol'
class leq(MathSymbol): unicode = unichr(8804)
class le(MathSymbol): unicode = unichr(8804)
class prec(MathSymbol): unicode = unichr(8826)
class preceq(MathSymbol): unicode = unichr(8828)
class ll(MathSymbol): unicode = unichr(8810)
class subset(MathSymbol): unicode = unichr(8834)
class subseteq(MathSymbol): unicode = unichr(8838)
class sqsubseteq(MathSymbol): unicode = unichr(8849)
class In(MathSymbol):
    macroName = 'in'
class vdash(MathSymbol): unicode = unichr(8866)
class geq(MathSymbol): unicode = unichr(8805)
class ge(MathSymbol): unicode = unichr(8805)
class succ(MathSymbol): unicode = unichr(8827)
class succeq(MathSymbol): unicode = unichr(8829)
class gg(MathSymbol): unicode = unichr(8811)
class supset(MathSymbol): unicode = unichr(8835)
class supseteq(MathSymbol): unicode = unichr(8839)
class sqsupset(MathSymbol): unicode = unichr(8848)
class sqsupseteq(MathSymbol): unicode = unichr(8850)
class ni(MathSymbol): unicode = unichr(8715)
class dashv(MathSymbol): unicode = unichr(8867)
class equiv(MathSymbol): unicode = unichr(8801)
class sim(MathSymbol): unicode = unichr(8764)
class simeq(MathSymbol): unicode = unichr(8771)
class asymp(MathSymbol): unicode = unichr(8781)
class approx(MathSymbol): unicode = unichr(8776)
class cong(MathSymbol): unicode = unichr(8773)
class neq(MathSymbol): unicode = unichr(8800)
class ne(MathSymbol): unicode = unichr(8800)
class doteq(MathSymbol): unicode = unichr(8784)
class notin(MathSymbol): pass
class models(MathSymbol): unicode = unichr(8871)
class perp(MathSymbol): unicode = unichr(8869)
class mid(MathSymbol): unicode = unichr(8739)
class parallel(MathSymbol): unicode = unichr(8741)
class bowtie(MathSymbol): unicode = unichr(8904)
class Join(MathSymbol): pass
class smile(MathSymbol): unicode = unichr(8995)
class frown(MathSymbol): unicode = unichr(8994)
class propto(MathSymbol): unicode = unichr(8733)

#
# Table 3.6: Arrow Symbols
#

class leftarrow(MathSymbol): unicode = unichr(8592)
class Leftarrow(MathSymbol): unicode = unichr(8656)
class rightarrow(MathSymbol): unicode = unichr(8594)
class Rightarrow(MathSymbol): unicode = unichr(8658)
class leftrightarrow(MathSymbol): unicode = unichr(8596)
class Leftrightarrow(MathSymbol): unicode = unichr(8660)
class mapsto(MathSymbol): unicode = unichr(8614)
class hookleftarrow(MathSymbol): unicode = unichr(8617)
class leftharpoonup(MathSymbol): unicode = unichr(8636)
class leftharpoondown(MathSymbol): unicode = unichr(8637)
class rightleftharpoons(MathSymbol): unicode = unichr(8652)
class longleftarrow(MathSymbol): pass
class Longleftarrow(MathSymbol): pass
class longrightarrow(MathSymbol): pass
class Longrightarrow(MathSymbol): pass
class longleftrightarrow(MathSymbol): pass
class Longleftrightarrow(MathSymbol): pass
class longmapsto(MathSymbol): pass
class hookrightarrow(MathSymbol): unicode = unichr(8618)
class rightharpoonup(MathSymbol): unicode = unichr(8640)
class rightharpoondown(MathSymbol): unicode = unichr(8641)
class leadsto(MathSymbol): pass
class uparrow(MathSymbol): unicode = unichr(8593)
class Uparrow(MathSymbol): unicode = unichr(8657)
class downarrow(MathSymbol): unicode = unichr(8595)
class Downarrow(MathSymbol): unicode = unichr(8659)
class updownarrow(MathSymbol): unicode = unichr(8597)
class Updownarrow(MathSymbol): unicode = unichr(8661)
class nearrow(MathSymbol): unicode = unichr(8599)
class searrow(MathSymbol): unicode = unichr(8600)
class swarrow(MathSymbol): unicode = unichr(8601)
class nwarrow(MathSymbol): unicode = unichr(8598)

#
# Table 3.7: Miscellaneous Symbols
#

class aleph(MathSymbol): unicode = unichr(8501)
class hbar(MathSymbol): unicode = unichr(8463)
class imath(MathSymbol): pass
class jmath(MathSymbol): pass
class ell(MathSymbol): unicode = unichr(8467)
class wp(MathSymbol): unicode = unichr(8472)
class Re(MathSymbol): unicode = unichr(8476)
class Im(MathSymbol): unicode = unichr(8465)
class mho(MathSymbol): unicode = unichr(8487)
class prime(MathSymbol): unicode = unichr(8242)
class emptyset(MathSymbol): unicode = unichr(8709)
class nabla(MathSymbol): unicode = unichr(8711)
class surd(MathSymbol): unicode = unichr(8730)
class top(MathSymbol): unicode = unichr(8868)
class bot(MathSymbol): unicode = unichr(8869)
class VerticalBar(MathSymbol):
    macroName = '|'
class forall(MathSymbol): unicode = unichr(8704)
class exists(MathSymbol): unicode = unichr(8707)
class neg(MathSymbol): pass
class flat(MathSymbol): unicode = unichr(9837)
class natural(MathSymbol): unicode = unichr(9838)
class sharp(MathSymbol): unicode = unichr(9839)
class backslash(MathSymbol): unicode = unichr(92)
class partial(MathSymbol): unicode = unichr(8706)
class infty(MathSymbol): unicode = unichr(8734)
class Box(MathSymbol): pass
class Diamond(MathSymbol): pass
class triangle(MathSymbol): unicode = unichr(9653)
class clubsuit(MathSymbol): unicode = unichr(9827)
class diamondsuit(MathSymbol): unicode = unichr(9830)
class heartsuit(MathSymbol): unicode = unichr(9829)
class spadesuit(MathSymbol): unicode = unichr(9824)

#
# Table 3.8: Variable-sized Symbols
#

class sum(MathSymbol): unicode = unichr(8721)
class prod(MathSymbol): unicode = unichr(8719)
class coprod(MathSymbol): unicode = unichr(8720)
class int(MathSymbol): unicode = unichr(8747)
class oint(MathSymbol): unicode = unichr(8750)
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
