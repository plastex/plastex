#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX.Tokenizer import Node, Token
from plasTeX import Macro, Command, Environment
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

class mathshift(Macro):
    """ 
    The '$' character in TeX

    This macro detects whether this is a '$' or '$$' grouping.  If 
    it is the former, a 'math' environment is invoked.  If it is 
    the latter, a 'displaymath' environment is invoked.

    """
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

class alignmenttab(Macro):
    """ The '&' character in TeX """
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
    args = 'arg'
    def source(self):
        return '^%s' % sourcearguments(self)
    source = property(source)

class subscript(Macro):
    """ The '_' character in TeX """
    args = 'arg'
    def source(self):
        return '_%s' % sourcearguments(self)
    source = property(source)

class macroparameter(Macro):
    """ Paramaters for macros (i.e. #1, #2, etc.) """
    def invoke(self, tex):
        raise ValueError, 'Macro parameters should not be invoked'
    def source(self): 
        return '#'
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
    args = 'name:cs args:Args definition:nox'
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
        self.parse(tex)
        a = self.attributes
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
