#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX.Tokenizer import CC_MATHSHIFT, Node
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

    def invoke(self, tex):
        status.dot()

    def __repr__(self): return '\n\n'

class mbox(Command):
    """ Math box """
    args = 'self'
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
                displaymath.cmdmode = Macro.MODE_END
                tex.context.pop(displaymath)
            else:
                math.cmdmode = Macro.MODE_END
                tex.context.pop(math)
            return []

        for t in tex.itertokens():
            if t.catcode == CC_MATHSHIFT:
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
    def __repr__(self): 
        return '&'

class textvisiblespace(Macro):
    """ The '~' character in TeX """
    def __repr__(self): 
        return '~'

class superscript(Macro):
    """ The '^' character in TeX """
    args = 'self'
    def __repr__(self):
        return '^%s' % self.attributes.source

class subscript(Macro):
    """ The '_' character in TeX """
    args = 'self'
    def __repr__(self):
        return '_%s' % self.attributes.source

class macroparameter(Macro):
    """ Paramaters for macros (i.e. #1, #2, etc.) """
    def invoke(self, tex):
        raise ValueError, 'Macro parameters should not be invoked'
    def __repr__(self): 
        return '#'

class bgroup(Macro):
    def invoke(self, tex):
        tex.context.push()
    def __repr__(self):
        return '{'
    def digest(self, tokens):
        self.childNodes = []
        # Absorb the tokens that belong to us
        for item in tokens:
            if item.nodeType == Node.ELEMENT_NODE:
                if type(item) is egroup:
                    break
                item.digest(tokens)
            self.childNodes.append(item)
            item.parentNode = self
    def __repr__(self):
        if self.childNodes is not None:
            return '{%s}' % ''.join([repr(x) for x in self.childNodes])
        return '{'

class egroup(Macro):
    def invoke(self, tex):
        tex.context.pop()
    def __repr__(self):
        return '}'
    def digest(self, tokens):
        return

class _def(Macro):
    """ TeX's \\def command """
    local = True
    args = 'name:cs args:args definition:nox'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        deflog.debug('def %s %s %s', a['name'], a['args'], a['definition'])
        tex.context.newdef(a['name'], a['args'], a['definition'], local=self.local)

class x_def(_def): 
    texname = 'def'
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
    args = 'a:tok b:tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'] == a['b'])

class x_if(_if): 
    """ \\if """
    texname = 'if'
        
class ifnum(_if):
    """ Compare two integers """
    args = 'a:number rel:tok b:number'
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
    args = 'a:dimen rel:tok b:dimen'
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
    args = 'value:number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(not(not(self.attributes['value'] % 2)))

class ifeven(_if):
    """ Test for even integer """
    args = 'value:number'
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
    args = 'a:tok b:tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'].catcode == a['b'].catcode)

class ifx(_if):
    """ Test if tokens agree """
    args = 'a:xtok b:xtok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        return tex.getCase(a['a'] == a['b'])

class ifvoid(_if):
    """ Test a box register """
    args = 'value:number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifhbox(_if):
    """ Test a box register """
    args = 'value:number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifvbox(_if):
    """ Test a box register """
    args = 'value:number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(False)

class ifeof(_if):
    """ Test for end of file """
    args = 'value:number'
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
    args = 'value:number'
    def invoke(self, tex):
        self.parse(tex)
        return tex.getCase(self.attributes['value'])


class let(Macro):
    """ \\let """
    args = 'name:cs = value:tok'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.context.let(a['name'], a['value'])

class char(Macro):
    """ \\char """
    args = 'char:number'
    def invoke(self, tex):
        self.parse(tex)
        return [chr(self.attributes['char'])]

class catcode(Macro):
    """ \\catcode """
    args = 'char:number = code:number'
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        tex.context.catcode(chr(a['char']), a['code'])
    def __repr__(self):
        return '\\catcode`\%s=%s' % (chr(self.attributes['char']), 
                                     self.attributes['code'])

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
