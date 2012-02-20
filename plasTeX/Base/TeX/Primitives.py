#!/usr/bin/env python

import codecs
from plasTeX.Tokenizer import Token, EscapeSequence
from plasTeX import Command, Environment, CountCommand
from plasTeX import IgnoreCommand, sourceChildren
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

    @property
    def source(self): 
        if self.hasChildNodes():
            return '%s\n\n' % sourceChildren(self)
        return '\n\n'

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
        MathShift.inEnv.append(None)
        Command.parse(self, tex) 
        MathShift.inEnv.pop()
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
    inEnv = []

    def invoke(self, tex):
        """
        This gets a bit tricky because we need to keep track of both 
        our beginning and ending.  We also have to take into 
        account \mbox{}es.

        """
        inEnv = type(self).inEnv
        math = self.ownerDocument.createElement('math')
        displaymath = self.ownerDocument.createElement('displaymath')

        # See if this is the end of the environment
        if inEnv and inEnv[-1] is not None:
            env = inEnv.pop()
            if type(env) is type(displaymath):
                for t in tex.itertokens():
                    break
                displaymath.macroMode = Command.MODE_END
                self.ownerDocument.context.pop(displaymath)
                return [displaymath]
            else:
                math.macroMode = Command.MODE_END
                self.ownerDocument.context.pop(math)
                return [math]

        for t in tex.itertokens():
            if t.catcode == Token.CC_MATHSHIFT:
                inEnv.append(displaymath)
            else:
                inEnv.append(math)
                tex.pushToken(t)
            break

        current = inEnv[-1]
        mathshiftlog.debug('%s (%s)' % (current.tagName, id(current)))
        self.ownerDocument.context.push(current)

        return [current]

class AlignmentChar(Command):
    """ The '&' character in TeX """
    macroName = 'active::&'

class SuperScript(Command):
    """ The '^' character in TeX """
    macroName = 'active::^'
    args = 'self'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not self.ownerDocument.context.isMathMode:
            return tex.textTokens('^')
        Command.parse(self, tex)

class SubScript(Command):
    """ The '_' character in TeX """
    macroName = 'active::_'
    args = 'self'
    def invoke(self, tex):
        # If we're not in math mode, just treat this as a normal character
        if not self.ownerDocument.context.isMathMode:
            return tex.textTokens('_')
        Command.parse(self, tex)

class DefCommand(Command):
    """ TeX's \\def command """
    local = True
    args = 'name:Tok args:Args definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        deflog.debug('def %s %s %s', a['name'], a['args'], a['definition'])
        # See if this definiton has nested parameters
        nested = False
        aiter = iter(a['args'])
        for t in aiter:
            if t.catcode == t.CC_PARAMETER:
                for t in aiter:
                    if t.catcode == t.CC_PARAMETER:
                        nested = True
                    break
            if nested:
                break
        # If we are nested, get rid of one level of #s
        if nested:
            for key in ['args','definition']:
                params = 0
                newarg = []
                for t in a[key]:
                    if t.catcode == t.CC_PARAMETER:
                        params += 1
                        newarg.append(t)
                    else:
                        if params > 1:
                            newarg.pop()
                        newarg.append(t)
                        params = 0
                a[key] = newarg
        self.ownerDocument.context.newdef(a['name'], a['args'], a['definition'], local=self.local)

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
        tex.processIfContent(a['a'] == a['b'])
        return []

class else_(Command):
    macroName = 'else'

class fi(Command): 
    pass
        
class ifnum(IfCommand):
    """ Compare two integers """
    args = 'a:Number rel:Tok'
    def invoke(self, tex):
        self.parse(tex)
        attrs = self.attributes
        attrs['b'] = tex.readNumber(optspace=False)
        relation = attrs['rel']
        a, b = attrs['a'], attrs['b']
        if relation == '<':
            tex.processIfContent(a < b)
            return []
        elif relation == '>':
            tex.processIfContent(a > b)
            return []
        elif relation == '=':
            tex.processIfContent(a == b)
            return []
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
            tex.processIfContent(a < b)
            return []
        elif relation == '>':
            tex.processIfContent(a > b)
            return []
        elif relation == '=':
            tex.processIfContent(a == b)
            return []
        raise ValueError, '"%s" is not a valid relation' % relation

class ifodd(IfCommand):
    """ Test for odd integer """   
    def invoke(self, tex):
        tex.processIfContent(not(not(tex.readNumber(optspace=False) % 2)))
        return []

class ifeven(IfCommand):
    """ Test for even integer """
    def invoke(self, tex):
        tex.processIfContent(not(tex.readNumber(optspace=False) % 2))
        return []

class ifvmode(IfCommand):
    """ Test for vertical mode """
    def invoke(self, tex):
        tex.processIfContent(False)
        return []

class ifhmode(IfCommand):
    """ Test for horizontal mode """
    def invoke(self, tex):
        tex.processIfContent(True)
        return []

class ifmmode(IfCommand):
    """ Test for math mode """
    def invoke(self, tex):
        tex.processIfContent(self.ownerDocument.context.isMathMode)
        return []

class ifinner(IfCommand):
    """ Test for internal mode """
    def invoke(self, tex):
        tex.processIfContent(False)
        return []

class ifcat(IfCommand):
    """ Test if category codes agree """
    args = 'a:Tok b:Tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.processIfContent(a['a'].catcode == a['b'].catcode)
        return []

class ifx(IfCommand):
    """ Test if tokens agree """
    args = 'a:XTok b:XTok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.processIfContent(a['a'] == a['b'])
        return []

class ifvoid(IfCommand):
    """ Test a box register """
    def invoke(self, tex):
        tex.readNumber(optspace=False)
        tex.processIfContent(False)
        return []

class ifhbox(IfCommand):
    """ Test a box register """
    def invoke(self, tex):
        tex.readNumber(optspace=False)
        tex.processIfContent(False)
        return []

class ifvbox(IfCommand):
    """ Test a box register """
    def invoke(self, tex):
        tex.readNumber(optspace=False)
        tex.processIfContent(False)
        return []

class ifeof(IfCommand):
    """ Test for end of file """
    def invoke(self, tex):
        tex.readNumber(optspace=False)
        tex.processIfContent(False)
        return []

class iftrue(IfCommand):
    """ Always true """
    def invoke(self, tex):
        tex.processIfContent(True)
        return []

class ifplastex(iftrue): pass
class plastexfalse(Command): pass
class plastextrue(Command): pass

class ifhtml(iftrue): pass
class htmlfalse(Command): pass
class htmltrue(Command): pass

class iffalse(IfCommand):
    """ Always false """
    def invoke(self, tex):
        tex.processIfContent(False)
        return []

class ifpdf(iffalse): pass
class pdffalse(Command): pass
class pdftrue(Command): pass
#class pdfoutput(Command): pass

class ifcase(IfCommand):
    """ Cases """
    def invoke(self, tex):
        tex.processIfContent(tex.readNumber(optspace=False))
        return []


class let(Command):
    """ \\let """
    args = 'name:Tok = value:Tok'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.let(a['name'], a['value'])

class char(Command):
    """ \\char """
    args = 'char:Number'
    def invoke(self, tex):
        return tex.textTokens(chr(self.parse(tex)['char']))

class chardef(Command):
    args = 'command:cs = num:Number'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.chardef(a['command'], a['num'])
      
class NameDef(Command):
    macroName = '@namedef'
    args = 'name:str value:nox'

class makeatletter(Command):
    def invoke(self, tex):
        self.ownerDocument.context.catcode('@', Token.CC_LETTER)

class everypar(Command):
    args = 'tokens:nox'

class catcode(Command):
    """ \\catcode """
    args = 'char:Number = code:Number'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.catcode(chr(a['char']), a['code'])
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
            path = tex.kpsewhich(a['name'])

            status.info(' ( %s ' % path)
            encoding = self.config['files']['input-encoding']
            tex.input(codecs.open(path, 'r', encoding, 'replace'))
            status.info(' ) ')

        except (OSError, IOError), msg:
            log.warning(msg)
            status.info(' ) ')

class endinput(Command):
    def invoke(self, tex):
        tex.endInput()

class include(input):
    """ \\include """

class showthe(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        log.info(self.ownerDocument.createElement(self.parse(tex)['arg']).the())


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

class jobname(Command):
    def invoke(self, tex):
        self.unicode = tex.jobname

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
            nexttok = tok
            break
        for tok in tex:
            aftertok = tok
            break
        tex.pushToken(aftertok)
        tex.pushToken(nexttok)
        return []

class vskip(Command):
    args = 'size:Dimen'

class hskip(Command):
    args = 'size:Dimen'

class openout(Command):
    args = 'arg:cs = value:any'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.newwrite(a['arg'].nodeName, 
#                                           a['value'].textContent)
        return result

class closeout(Command):
    args = 'arg:cs'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.writes[a['arg'].nodeName].close()
        return result

class write(Command):
    args = 'arg:cs text:nox'
    def invoke(self, tex):
        result = Command.invoke(self, tex)
#       a = self.attributes
#       self.ownerDocument.context.writes[a['arg'].nodeName].write(self.attributes['text']+'\n')
        return result

class protected_write(write):
    nodeName = 'protected@write'

class hfil(Command):
    pass
