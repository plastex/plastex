#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.TeX import TeX, flatten
from plasTeX.Context import Macro

class ListFlattening(TestCase):

    def simple(self):
        input = ['a', ['b', ['c']], 'd']
        output = ['a', 'b', 'c', 'd']
        assert output == flatten(input)

class Dimensions(TestCase):

    def testLength(self):
        s = TeX('-6.00 pt +2 in 3.0mm')
        length = s.readDimen()
        assert (length - (-6.0)) < 0.01, '"%s" != "%s"' % (length, -6.0)
        length = s.readDimen()
        assert (length - 144.54) < 0.01, '"%s" != "%s"' % (length, 144.54)
        length = s.readDimen()
        assert (length - 8.5358) < 0.01, '"%s" != "%s"' % (length, 8.5358)

class Glue(TestCase):
 
    def testGlue(self):
        s = TeX('-6 pt plus 4in foo')
        glue = s.readGlue()
        assert (glue - (-6.0)) < 0.01, '"%s" != "%s"' % (glue, -6.0)
        assert (glue.stretch - 289.079) < 0.01, '"%s" != "%s"' % (glue.stretch, 289.079)
        assert (glue.shrink - 0.0) < 0.01, '"%s" != "%s"' % (glue.shrink, 0.0)

class SimpleParsing(TestCase):

    def testParagraphCompression(self):
        s = TeX('\\par \n\n\n \\par \\par a\n\n\n hi \\par \n\n \\par ')
        tokens = s.parse()
        assert len(tokens) == 5
        assert tokens[1] == 'a', '"%s" != "%s"' % (tokens[1], 'a')
        assert tokens[3] == 'hi ', '"%s" != "%s"' % (tokens[3], 'hi ')
    
    def testPlainString(self):
        s = TeX('a b c')
        assert 'a' == s.getToken()
        assert ' ' == s.getToken()
        assert 'b' == s.getToken()
        assert ' ' == s.getToken()
        assert 'c' == s.getToken()

    def testTokenGroupings(self):
        s = TeX('{foo {x{foo bar}} y} {a}')
        output = [['foo xfoo bar y'], ' ', ['a']]
        tok = s.getToken()
        assert output[0] == tok, '"%s" != "%s"' % (output[0], tok) 
        tok = s.getToken()
        assert output[1] == tok, '"%s" != "%s"' % (output[1], tok) 
        tok = s.getToken()
        assert output[2] == tok, '"%s" != "%s"' % (output[2], tok) 

    def testFloats(self):
        s = TeX('-2.56 6.0245 400')
        assert (-2.56 - s.getFloat()) < 0.000001
        assert (6.0245 - s.getFloat()) < 0.000001
        assert (400 - s.getFloat()) < 0.000001

    def testIntegers(self):
        s = TeX('21 +6 -321')
        assert 21 == s.getInteger()
        assert 6 == s.getFloat()
        assert -321 == s.getInteger()

    def testComments(self):
        s = TeX('''
a
% This is a comment
b % this is also a comment
{c}
% Yet another comment
''')
        for output in [' ', 'a', ' ', 'b', ' ', ['c']]:
            tok = s.getToken()
            assert output == tok, '"%s" != "%s"' % (output, tok)

    def testGroupings(self):
        s = TeX('[foo[tw{o}]] (bar) < {hi} >')

        output = ['foo[two]']
        group = s.getGroup()
        assert output == group, '"%s" != "%s"' % (output, group)

        output = ['bar']
        group = s.getGroup('()')
        assert output == group, '"%s" != "%s"' % (output, group)

        output = None
        group = s.getGroup()
        assert output == group, '"%s" != "%s"' % (output, group)

        output = ['hi ']
        group = s.getGroup('<>')
        assert output == group, '"%s" != "%s"' % (output, group)

    def testInlineVerbatim(self):
        s = TeX('verbatim {text}+ foobar')
        assert 'verbatim {text}' == s.getVerbatim('+', strip_end=True)
        assert ' foobar' == s.read()
   
    def testVerbatim(self):
        s = TeX('this is % verbatim # text\n\\end{verbatim} foobar')
        assert 'this is % verbatim # text\n' == s.getVerbatim('\\end{verbatim}', strip_end=True)
        assert ' foobar' == s.read()

    def testEnvironmentName(self):
        s = TeX('{tabular*}')
        assert ['tabular*'] == s.getToken()

    def testMacro(self):
        class foobar(Macro):
            def parse(self, tex):
                self.opt = tex.getArgument('[]')
                self.arg = tex.getArgument() 
                return self
        s = TeX(r'\foobar[opt]{this is some {content}}')
        s.context['foobar'] = foobar
        output = s.parse()[0]
        assert type(output) == foobar, '"%s" != foobar' % (type(output[0]))
        assert output.opt == ['opt']
        assert output.arg == ['this is some content']
        assert s.read() == ''

    def testMixedContent(self):
        s = TeX('a {b} c')
        output = ['a b c']
        parsed = s.parse()
        assert output == parsed, '"%s" != "%s"' % (output, parsed)
   
    def testMacroArgs(self):
        s = TeX('(2)[foo]{this is the macro content}')
        assert None == s.getArgument('<>')
        assert ['2'] == s.getArgument('()')
        assert ['foo'] == s.getArgument('[]')
        assert ['this is the macro content'] == s.getArgument()

    def testParagraphs(self):
        s = TeX('''
par1

% comment



par2


par3

''')
        output = s.parse()
        assert len(output) == 6, 'len of %s is not 6' % output
        assert output[0] == ' par1' 
        assert output[2] == 'par2' 
        assert output[4] == 'par3' 

    def testSuperscripts(self):
        s = TeX('^{2_{x}}')
        assert type(s.parse()[0]) is type(s.context['superscript'])

    def testSubscripts(self):
        s = TeX('_{2^{x}}')
        assert type(s.parse()[0]) is type(s.context['subscript'])

    def testSpecialCharacters(self):
        s = TeX('& $ ~')
        output = s.parse()
        assert type(output[0]) is type(s.context['alignmenttab'])
        assert output[1] == ' '
        assert type(output[2]) is type(s.context['math'])
        assert output[3] == ' '
        assert type(output[4]) is type(s.context['textvisiblespace'])

    def testEnvironment(self):
        class foobar(Macro):
            args = '[ opt ] arg'
        s = TeX(r'''\begin{foobar}[2]{test content} 
environment content
\end{foobar}''')
        s.context['foobar'] = foobar
        output = s.parse()
        assert output[0] is output[-1]
        assert output[1].strip() == 'environment content'

    def testInvalidEnvironment(self):
        class foobar(Macro):
            args = '[ opt ] arg'
        s = TeX(r'''\begin{foobar}[2]{test content}
environment content
\end{foo}''')
        s.context['foobar'] = foobar
        output = s.parse()
        assert len(output) == 3, output
        assert type(output[0]) == foobar, '"%s" != "%s"' % \
               (type(output[0]), foobar)

if __name__ == '__main__':
    unittest.main()

