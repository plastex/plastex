#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX.Token import *
from plasTeX import Macro, Command, Environment
from plasTeX.Logging import getLogger

log = getLogger()
status = getLogger('status')
deflog = getLogger('parse.definitions')
envlog = getLogger('parse.environments')
mathshiftlog = getLogger('parse.mathshift')

class par(Macro):
    """ Paragraph """
    level = PARAGRAPH
    def invoke(self, tex):
        status.dot()
#       tex.context.push(self)
        return [self]
    def __repr__(self): return '\n\n'

class mbox(Command):
    """ Math box """
    args = 'self'
    def parse(self, tex):
        shifted = 0
        if mathshift.inenv:
            shifted = 1
            mathshift.inenv.append(None)
        tokens = Command.parse(self, tex) 
        if shifted:
            mathshift.inenv.pop()
        return tokens

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
                tex.next()
            tex.context.pop(env)
            return [env]

        for t in tex.itertokens():
            if t.code == CC_MATHSHIFT:
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
        return '^{%s}' % ''.join([repr(x) for x in self])

class subscript(Macro):
    """ The '_' character in TeX """
    args = 'self'
    def __repr__(self): 
        return '_{%s}' % ''.join([repr(x) for x in self])

class macroparameter(Macro):
    """ Paramaters for macros (i.e. #1, #2, etc.) """
    def invoke(self, tex):
        raise ValueError, 'Macro parameters should not be invoked'
    def __repr__(self): 
        return '#'

class bgroup(Macro):
    def invoke(self, tex):
        self.context.push()
        return [self]
    def __repr__(self):
        return '{'

class egroup(Macro):
    def invoke(self, tex):
        self.context.pop()
        return [self]
    def __repr__(self):
        return '}'

class _def(Macro):
    """
    TeX's \\def command

    """
    local = True
    def invoke(self, tex):

        name = tex.getArgument(type='cs')

        # Get argument string
        args = []
        for t in tex.itertokens():
            if t.code == CC_BGROUP:
                tex.pushtoken(t)
                break
            else:
                args.append(t) 
        else: pass

        # Parse definition from stream
        definition = tex.getArgument()

        deflog.debug('def %s %s %s', name, args, definition)
        tex.context.newdef(name, args, definition, local=self.local)

        return [self]

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
        Macro.parse(self, tex)
        tex.context.newif(self.attributes['name'])
        return [self]

class _if(Macro):
    """ Test if character codes agree """
    def invoke(self, tex):
        return tex.getCase(tex.getArgument()[0] == tex.getArgument()[0])

class x_if(_if): 
    """ \\if """
    texname = 'if'
        
class ifnum(_if):
    """ Compare two integers """
    def invoke(self, tex):
        a = tex.readInteger()
        relation = tex.getArgument(type='str')
        b = tex.readInteger()
        if relation == '<':
            return tex.getCase(a < b)
        elif relation == '>':
            return tex.getCase(a > b)
        elif relation == '=':
            return tex.getCase(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifdim(_if):
    """ Compare two dimensions """
    def invoke(self, tex):
        a = tex.readDimen()
        relation = tex.getArgument(type='str')
        b = tex.readDimen()
        if relation == '<':
            return tex.getCase(a < b)
        elif relation == '>':
            return tex.getCase(a > b)
        elif relation == '=':
            return tex.getCase(a == b)
        raise ValueError, '"%s" is not a valid relation' % relation

class ifodd(_if):
    """ Test for odd integer """
    def invoke(self, tex):
        return tex.getCase(not(not(tex.readInteger() % 2)))

class ifeven(_if):
    """ Test for even integer """
    def invoke(self, tex):
        return tex.getCase(not(tex.readInteger() % 2))

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
    def invoke(self, tex):
        return tex.getCase(tex.getArgument()[0].code == tex.getArgument()[0].code)

class ifx(_if):
    """ Test if tokens agree """
    def invoke(self, tex):
        return tex.getCase(tex.getArgument()[0] == tex.getArgument()[0])

class ifvoid(_if):
    """ Test a box register """
    def invoke(self, tex):
        a = tex.readInteger()
        return tex.getCase(False)

class ifhbox(_if):
    """ Test a box register """
    def invoke(self, tex):
        a = tex.readInteger()
        return tex.getCase(False)

class ifvbox(_if):
    """ Test a box register """
    def invoke(self, tex):
        a = tex.readInteger()
        return tex.getCase(False)

class ifeof(_if):
    """ Test for end of file """
    def invoke(self, tex):
        a = tex.readInteger()
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
    def invoke(self, tex):
        return tex.getCase(tex.readInteger())


class let(Macro):
    """ \\let """
    args = 'name:cs = value'
    def invoke(self, tex):
        Macro.parse(self, tex)
        a = self.attributes
        tex.context[a['name']] = type(tex.context[a['value']])
        return [self]

class char(Macro):
    """ \\char """
    def invoke(self, tex):
        return [chr(tex.readInteger())]

class catcode(Macro):
    """ \\catcode """
    def invoke(self, tex):
        for t in tex.itertokens():
            if t == '`':
                continue
            break
        tex.getArgument('=')
        number = tex.readInteger() 
        tex.context.catcode(t,number)
        return [self]

class advance(Command):
    """ \\advance """
    def invoke(self, tex):
        l = tex.getArgument()
        tex.getArgument('by')
        by = tex.getDimension()
        return [self]

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
        attrs = self.attributes
        Command.parse(self, tex)
        tokens = []
        try: 
            #path = kpsewhich(attrs['name'])
            path = attrs['name']

            status.info(' ( %s.tex ' % attrs['name'])
            tex.input(open(path, 'r'))
            status.info(' ) ')

        except (OSError, IOError):
            log.warning('\nProblem opening file "%s"', attrs['name'])
            status.info(' ) ')
        return tokens

class include(input):
    """ \\include """
