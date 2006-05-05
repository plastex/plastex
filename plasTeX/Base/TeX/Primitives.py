#!/usr/bin/env python

import codecs
from plasTeX.Tokenizer import Token, EscapeSequence
from plasTeX import Command, Environment, CountCommand
from plasTeX import IgnoreCommand, sourcechildren
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')

class relax(Command):
    pass

class protect(Command):
    pass

class global_(Command):
    macroName = 'global'

class par(Command):
    """ Paragraph """
    level = Command.PAR_LEVEL

    def invoke(self, tex):
        status.dot()

    def source(self): 
        if self.hasChildNodes():
            return '%s\n\n' % sourcechildren(self)
        return '\n\n'
    source = property(source)

    def digest(self, tokens):
        status.dot()

    @property
    def isElementContentWhitespace(self):
        if not self.hasChildNodes():
            return True
        return False

class BoxCommand(Command):
    """ Base class for box-type commands """
    args = 'self'
    mathMode = False
    def parse(self, tex):
        MathShift.inenv.append(None)
        Command.parse(self, tex) 
        MathShift.inenv.pop()
        return self.attributes

class hbox(BoxCommand): pass
class vbox(BoxCommand): pass

class MathShift(Command):
    """ 
    The '$' character in TeX

    This macro detects whether this is a '$' or '$$' grouping.  If 
    it is the former, a 'math' environment is invoked.  If it is 
    the latter, a 'displaymath' environment is invoked.

    """
    macroName = 'active::$'
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
                displaymath.macroMode = Command.MODE_END
                tex.context.pop(displaymath)
                return [displaymath]
            else:
                math.macroMode = Command.MODE_END
                tex.context.pop(math)
                return [math]

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

class AlignmentChar(Command):
    """ The '&' character in TeX """
    macroName = 'active::&'

class SuperScript(Command):
    """ The '^' character in TeX """
    macroName = 'active::^'
    args = 'arg'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not tex.context.isMathMode:
            return tex.texttokens('^')
        Command.parse(self, tex)

class SubScript(Command):
    """ The '_' character in TeX """
    macroName = 'active::_'
    args = 'arg'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not tex.context.isMathMode:
            return tex.texttokens('_')
        Command.parse(self, tex)

class DefCommand(Command):
    """ TeX's \\def command """
    local = True
    args = 'name:Tok args:Args definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        deflog.debug('def %s %s %s', a['name'], a['args'], a['definition'])
        tex.context.newdef(a['name'], a['args'], a['definition'], local=self.local)

class def_(DefCommand): 
    macroName = 'def'

class edef(DefCommand):
    local = True

class xdef(DefCommand):
    local = False

class gdef(DefCommand):
    local = False

class IfCommand(Command):
    pass

class if_(IfCommand): 
    """ \\if """
    args = 'a:Tok b:Tok'
    macroName = 'if'
    """ Test if character codes agree """
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.readIfContent(a['a'] == a['b'])

class else_(Command):
    macroName = 'else'

class fi(Command): 
    pass
        
class ifnum(IfCommand):
    """ Compare two integers """
    args = 'a:Number rel:Tok b:Number'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.readIfContent(a < b)
        elif relation == '>':
            return tex.readIfContent(a > b)
        elif relation == '=':
            return tex.readIfContent(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifdim(IfCommand):
    """ Compare two dimensions """
    args = 'a:Dimen rel:Tok b:Dimen'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            return tex.readIfContent(a < b)
        elif relation == '>':
            return tex.readIfContent(a > b)
        elif relation == '=':
            return tex.readIfContent(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifodd(IfCommand):
    """ Test for odd integer """   
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(not(not(self.attributes['value'] % 2)))

class ifeven(IfCommand):
    """ Test for even integer """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(not(self.attributes['value'] % 2))

class ifvmode(IfCommand):
    """ Test for vertical mode """
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(False)

class ifhmode(IfCommand):
    """ Test for horizontal mode """
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(True)

class ifmmode(IfCommand):
    """ Test for math mode """
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(tex.context.isMathMode)

class ifinner(IfCommand):
    """ Test for internal mode """
    def invoke(self, tex):
        return tex.readIfContent(False)

class ifcat(IfCommand):
    """ Test if category codes agree """
    args = 'a:Tok b:Tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.readIfContent(a['a'].catcode == a['b'].catcode)

class ifx(IfCommand):
    """ Test if tokens agree """
    args = 'a:XTok b:XTok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.readIfContent(a['a'] == a['b'])

class ifvoid(IfCommand):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(False)

class ifhbox(IfCommand):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(False)

class ifvbox(IfCommand):
    """ Test a box register """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(False)

class ifeof(IfCommand):
    """ Test for end of file """
    args = 'value:Number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(False)

class iftrue(IfCommand):
    """ Always true """
    def invoke(self, tex):
        self.parse(tex)
        return tex.readIfContent(True)

class ifplastex(iftrue): pass
class plastexfalse(Command): pass
class plastextrue(Command): pass

class ifhtml(iftrue): pass
class htmlfalse(Command): pass
class htmltrue(Command): pass

class iffalse(IfCommand):
    """ Always false """
    def invoke(self, tex):
        return tex.readIfContent(False)

#class ifpdf(iffalse): pass
#class pdffalse(Command): pass
#class pdftrue(Command): pass
#class pdfoutput(Command): pass

class ifcase(IfCommand):
    """ Cases """
    args = 'value:Number'
    def invoke(self, tex):
        return tex.readIfContent(self.parse(tex)['value'])


class let(Command):
    """ \\let """
    args = 'name:Tok = value:Tok'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.let(a['name'], a['value'])

class char(Command):
    """ \\char """
    args = 'char:Number'
    def invoke(self, tex):
        return tex.texttokens(chr(self.parse(tex)['char']))

class chardef(Command):
    args = 'command:cs = num:Number'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.chardef(a['command'], a['num'])
      
class NameDef(Command):
    macroName = '@namedef'
    args = 'name:str value:nox'

class makeatletter(Command):
    def invoke(self, tex):
        tex.context.catcode('@', Token.CC_LETTER)

class everypar(Command):
    args = 'tokens:nox'

class catcode(Command):
    """ \\catcode """
    args = 'char:Number = code:Number'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.catcode(chr(a['char']), a['code'])
    def source(self):
        return '\\catcode`\%s=%s' % (chr(self.attributes['char']), 
                                     self.attributes['code'])
    source = property(source)

class csname(Command):
    """ \\csname """
    def invoke(self, tex):
        name = []
        for t in tex:
            if t.nodeType == Command.ELEMENT_NODE and t.nodeName == 'endcsname':
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
            path = tex.kpsewhich(a['name'], self.config)

            status.info(' ( %s ' % path)
            encoding = self.config['files']['input-encoding']
            tex.input(codecs.open(path, 'r', encoding))
            status.info(' ) ')

        except (OSError, IOError), msg:
            log.warning(msg)
            status.info(' ) ')

class endinput(Command):
    def invoke(self, tex):
        tex.endinput()

class include(input):
    """ \\include """

class showthe(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        log.info(tex.context[self.parse(tex)['arg']].the())


class active(CountCommand):
    value = CountCommand.new(13)

class advance(Command):
    def invoke(self, tex):
        tex.readArgument(type='Number')
        tex.readKeyword(['by'])
        tex.readArgument(type='Number')

class leavevmode(Command): pass
class kern(Command): pass
class hrule(Command): pass
class jobname(Command): pass
class long(Command): pass
class undefined(Command): pass
class undefined_(Command):
    macroName = '@undefined'
class vobeyspaces_(Command):
    macroName = '@vobeyspaces'
class noligs_(Command):
    macroName = '@noligs'

class expandafter(Command):
    def invoke(self, tex):
        nexttok = None
        for tok in tex.itertokens():
            nextok = tok
            break
        for tok in tex:
            aftertok = tok
            break
        tex.pushtoken(aftertok)
        tex.pushtoken(nexttok)
        return []

class vskip(Command):
    args = 'size:Dimen'

class hskip(Command):
    args = 'size:Dimen'

class openout(IgnoreCommand):
    args = 'arg:cs = value'

class newwrite(IgnoreCommand):
    args = 'arg:cs'

class write(IgnoreCommand):
    args = 'arg:cs text:nox'
