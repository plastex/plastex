#!/usr/bin/env python

from datetime import datetime
from plasTeX.Utils import *
from plasTeX.Tokenizer import Node, Token
from plasTeX import Macro, Command, Environment
from plasTeX import Parameter, Count, Dimen, MuDimen, Glue, MuGlue
from plasTeX import count, dimen, mudimen, glue, muglue
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')

class par(Macro):
    """ Paragraph """
    level = Node.PARAGRAPH_LEVEL
    isElementContentWhitespace = True

    def invoke(self, tex):
        status.dot()

    def source(self): 
        return '\n\n'
    source = property(source)

class mbox(Command):
    """ Math box """
    args = 'text'
    def parse(self, tex):
        shifted = 0
        if mathshift.inenv:
            shifted = 1
            mathshift.inenv.append(None)
        Command.parse(self, tex) 
        if shifted:
            mathshift.inenv.pop()
        return self.attributes

class mathshift(Macro):
    """ 
    The '$' character in TeX

    This macro detects whether this is a '$' or '$$' grouping.  If 
    it is the former, a 'math' environment is invoked.  If it is 
    the latter, a 'displaymath' environment is invoked.

    """
    macroName = 'core::$'
    inenv = []

    def invoke(self, tex):
        """
        This gets a bit tricky because we need to keep track of both 
        our beginning and ending.  We also have to take into 
        account \mbox{}es.

        """
        inenv = type(self).inenv
        math = tex.context['math']
        displaymath = tex.context['displaymath']

        # See if this is the end of the environment
        if inenv and inenv[-1] is not None:
            env = inenv.pop()
            if type(env) is type(displaymath):
                for t in tex.itertokens():
                    break
                displaymath.macroMode = Macro.MODE_END
                tex.context.pop(displaymath)
            else:
                math.macroMode = Macro.MODE_END
                tex.context.pop(math)
            return []

        for t in tex.itertokens():
            if t.catcode == Token.CC_MATHSHIFT:
                inenv.append(displaymath)
            else:
                inenv.append(math)
                tex.pushtoken(t)
            break

        current = inenv[-1]
        mathshiftlog.debug('%s (%s)' % (current.tagName, id(current)))
        tex.context.push(current)

        return [current]

class ampersand(Macro):
    """ The '&' character in TeX """
    macroName = 'core::&'
    def source(self): 
        return '&'
    source = property(source)

class textvisiblespace(Macro):
    """ The '~' character in TeX """
    def source(self): 
        return '~'
    source = property(source)

class superscript(Macro):
    """ The '^' character in TeX """
    macroName = 'core::^'
    args = 'arg'
    def source(self):
        return '^%s' % sourcearguments(self)
    source = property(source)

class subscript(Macro):
    """ The '_' character in TeX """
    macroName = 'core::_'
    args = 'arg'
    def source(self):
        return '_%s' % sourcearguments(self)
    source = property(source)

class bgroup(Macro):

    def invoke(self, tex):
        tex.context.push()

    def digest(self, tokens):
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.nodeType == Node.ELEMENT_NODE:
                if type(item) is egroup:
                    break
                item.digest(tokens)
            self.appendChild(item)

    def source(self):
        if self.childNodes:
            return '{%s}' % sourcechildren(self)
        return '{'
    source = property(source)

class egroup(Macro):
    def invoke(self, tex):
        tex.context.pop()
    def source(self):
        return '}'
    source = property(source)
    def digest(self, tokens):
        return

class _def(Macro):
    """ TeX's \\def command """
    local = True
    args = 'name:Tok args:Args definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        deflog.debug('def %s %s %s', a['name'], a['args'], a['definition'])
        tex.context.newdef(a['name'], a['args'], a['definition'], local=self.local)

class x_def(_def): 
    macroName = 'def'
class edef(_def):
    local = True
class xdef(_def):
    local = False
class gdef(_def):
    local = False

class newif(Macro):
    """ \\newif """
    args = 'name:cs'
    def invoke(self, tex):
        self.parse(tex)
        tex.context.newif(self.attributes['name'])

class _if(Macro):
    """ Test if character codes agree """
    args = 'a:Tok b:Tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'] == a['b'])

class x_if(_if): 
    """ \\if """
    macroName = 'if'
        
class ifnum(_if):
    """ Compare two integers """
    args = 'a:Number rel:Tok b:Number'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.getCase(a < b)
        elif relation == '>':
            return tex.getCase(a > b)
        elif relation == '=':
            return tex.getCase(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifdim(_if):
    """ Compare two dimensions """
    args = 'a:Dimen rel:Tok b:Dimen'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.getCase(a < b)
        elif relation == '>':
            return tex.getCase(a > b)
        elif relation == '=':
            return tex.getCase(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifodd(_if):
    """ Test for odd integer """   
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(not(not(self.attributes['value'] % 2)))

class ifeven(_if):
    """ Test for even integer """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(not(self.attributes['value'] % 2))

class ifvmode(_if):
    """ Test for vertical mode """
    def invoke(self, tex):
        return tex.getCase(False)

class ifhmode(_if):
    """ Test for horizontal mode """
    def invoke(self, tex):
        return tex.getCase(True)

class ifmmode(_if):
    """ Test for math mode """
    def invoke(self, tex):
        return tex.getCase(False)

class ifinner(_if):
    """ Test for internal mode """
    def invoke(self, tex):
        return tex.getCase(False)

class ifcat(_if):
    """ Test if category codes agree """
    args = 'a:Tok b:Tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'].catcode == a['b'].catcode)

class ifx(_if):
    """ Test if tokens agree """
    args = 'a:XTok b:XTok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'] == a['b'])

class ifvoid(_if):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifhbox(_if):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifvbox(_if):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifeof(_if):
    """ Test for end of file """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class iftrue(_if):
    """ Always true """
    def invoke(self, tex):
        return tex.getCase(True)

class iffalse(_if):
    """ Always false """
    def invoke(self, tex):
        return tex.getCase(False)

class ifcase(_if):
    """ Cases """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(self.attributes['value'])


class let(Macro):
    """ \\let """
    args = 'name:Tok = value:Tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.context.let(a['name'], a['value'])

class char(Macro):
    """ \\char """
    args = 'char:Number'
    def invoke(self, tex):
        self.parse(tex)
        return [chr(self.attributes['char'])]

class catcode(Macro):
    """ \\catcode """
    args = 'char:Number = code:Number'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.context.catcode(chr(a['char']), a['code'])
    def source(self):
        return '\\catcode`\%s=%s' % (chr(self.attributes['char']), 
                                     self.attributes['code'])
    source = property(source)

class advance(Command):
    """ \\advance """
    def invoke(self, tex):
        l = tex.getArgument()
        tex.getArgument('by')
        by = tex.getDimension()

class csname(Command):
    """ \\csname """
    def invoke(self, tex):
        name = []
        for t in tex.itertokens():
            if t == 'endcsname':
                break
            name.append(t)
        return [EscapeSequence(''.join(name))]

class endcsname(Command): 
    """ \\endcsname """
    pass

class input(Command):
    """ \\input """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        try: 
            #path = kpsewhich(attrs['name'])
            path = a['name']

            status.info(' ( %s.tex ' % path)
            tex.input(open(path, 'r'))
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nProblem opening file "%s"', path)
            status.info(' ) ')

class endinput(Command):
    def invoke(self, tex):
        tex.endinput()

class include(input):
    """ \\include """

class showthe(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        print tex.context[self.parse(tex)['arg']].the()


class newdimen(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        tex.context.newdimen(self.parse(tex)['arg'])

#
# TeX parameters (see The TeXbook, page 272)
#

# Integer parameters
class pretolerance(Parameter): value = count(100)
class tolerance(Parameter): value = count(200)
class hbadness(Parameter): value = count(1000)
class vbadness(Parameter): value = count(1000)
class linepenalty(Parameter): value = count(1000)
class hyphenpenalty(Parameter): value = count(50)
class exhyphenpenalty(Parameter): value = count(50)
class binoppenalty(Parameter): value = count(700)
class relpenalty(Parameter): value = count(500)
class clubpenalty(Parameter): value = count(150)
class widowpenalty(Parameter): value = count(150)
class displaywidowpenalty(Parameter): value = count(50)
class brokenpenalty(Parameter): value = count(100)
class predisplaypenalty(Parameter): value = count(10000)
class postdisplaypenalty(Parameter): value = count(0)
class interlinepenalty(Parameter): value = count(0)
class floatingpenalty(Parameter): value = count(0)
class outputpenalty(Parameter): value = count(0)
class doublehyphendemerits(Parameter): value = count(100000)
class finalhyphendemerits(Parameter): value = count(5000)
class adjdemerits(Parameter): value = count(10000)
class looseness(Parameter): value = count(0)
class pausing(Parameter): value = count(0)
class holdinginserts(Parameter): value = count(0)
class tracingonline(Parameter): value = count(0)
class tracingmacros(Parameter): value = count(0)
class tracingstats(Parameter): value = count(0)
class tracingparagraphs(Parameter): value = count(0)
class tracingpages(Parameter): value = count(0)
class tracingoutput(Parameter): value = count(0)
class tracinglostchars(Parameter): value = count(1)
class tracingcommands(Parameter): value = count(0)
class tracingrestores(Parameter): value = count(0)
class language(Parameter): value = count(0)
class uchyph(Parameter): value = count(1)
class lefthyphenmin(Parameter): value = count(0)
class righthyphenmin(Parameter): value = count(0)
class globaldefs(Parameter): value = count(0)
class defaulthyphenchar(Parameter): value = count(ord('-'))
class defaultskewchar(Parameter): value = count(-1)
class escapechar(Parameter): value = count(ord('\\'))
class endlinechar(Parameter): value = count(ord('\n'))
class newlinechar(Parameter): value = count(-1)
class maxdeadcycles(Parameter): value = count(0)
class hangafter(Parameter): value = count(0)
class fam(Parameter): value = count(0)
class mag(Parameter): value = count(0)
class delimiterfactor(Parameter): value = count(901)
class time(Parameter): value = count((datetime.now().hour*60) + datetime.now().minute)
class day(Parameter): value = count(datetime.now().day)
class month(Parameter): value = count(datetime.now().month)
class year(Parameter): value = count(datetime.now().year)
class showboxbreadth(Parameter): value = count(5)
class showboxdepth(Parameter): value = count(3)
class errorcontextlines(Parameter): value = count(5)

# Dimen parameters
class hfuzz(Dimen): value = dimen('0.1pt')
class vfuzz(Dimen): value = dimen('0.1pt')
class overfullrule(Dimen): value = dimen('5pt')
class emergencystretch(Dimen): value = dimen(0)
class hsize(Dimen): value = dimen('6.5in')
class vsize(Dimen): value = dimen('8.9in')
class maxdepth(Dimen): value = dimen('4pt')
class splitmaxdepth(Dimen): value = dimen('65536pt')
class boxmaxdepth(Dimen): value = dimen('65536pt')
class lineskipamount(Dimen): value = dimen(0)
class delimitershortfall(Dimen): value = dimen('5pt')
class nulldelimiterspace(Dimen): value = dimen('1.2pt')
class scriptspace(Dimen): value = dimen('0.5pt')
class mathsurround(Dimen): value = dimen(0)
class predisplaysize(Dimen): value = dimen(0)
class displaywidth(Dimen): value = dimen(0)
class displayindent(Dimen): value = dimen(0)
class parindent(Dimen): value = dimen('20pt')
class hangindent(Dimen): value = dimen(0)
class hoffset(Dimen): value = dimen(0)
class voffset(Dimen): value = dimen(0)

# Glue parameters
class baselineskip(Glue): value = glue(0)
class lineskip(Glue): value = glue(0)
class parskip(Glue): value = glue(0)
class abovedisplayskip(Glue): value = glue(0)
class abovedisplayshortskip(Glue): value = glue(0)
class belowdisplayskip(Glue): value = glue(0)
class belowdisplayshortskip(Glue): value = glue(0)
class leftskip(Glue): value = glue(0)
class rightskip(Glue): value = glue(0)
class topskip(Glue): value = glue(0)
class splittopskip(Glue): value = glue(0)
class tabskip(Glue): value = glue(0)
class spaceskip(Glue): value = glue(0)
class xspaceskip(Glue): value = glue(0)
class parfillskip(Glue): value = glue(0)

# MuGlue parameters
class thinmuskip(MuGlue): value = muglue(0)
class medmuskip(MuGlue): value = muglue(0)
class thickmuskip(MuGlue): value = muglue(0)

# Token parameters
#class output(Parameter): pass
#class everypar(Parameter): pass
#class everymath(Parameter): pass
#class everydisplay(Parameter): pass
#class everyhbox(Parameter): pass
#class everyvbox(Parameter): pass
#class everyjob(Parameter): pass
#class everycr(Parameter): pass
#class errhelp(Parameter): pass
