#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX import *
from plasTeX.TeX import TeX

class ArgumentParsing(TestCase):

    def testArgumentString(self):
        class foobar(Macro):
            args = 'arg1'
        arg = foobar().arguments
        expected = [Argument('arg1', {'expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString2(self):
        class foobar(Macro):
            args = '* [ opt ] arg1'
        arg = foobar().arguments
        expected = [Argument('*modifier*', {'spec':'*'}),
                    Argument('opt', {'spec':'[]','expanded':True}), 
                    Argument('arg1', {'expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString3(self):
        class foobar(Macro):
            args = '[ %opt ] @arg1'
        arg = foobar().arguments
        expected = [Argument('opt', {'spec':'[]','type':'dict','expanded':True}), 
                    Argument('arg1', {'type':'list','expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString4(self):
        class foobar(Macro):
            args = '[ %;opt ] @arg1'
        arg = foobar().arguments
        expected = [Argument('opt', {'spec':'[]','type':'dict','delim':';','expanded':True}), 
                    Argument('arg1', {'type':'list','expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString5(self):
        class foobar(Macro):
            args = '[ %;opt ] < arg1:str >'
        arg = foobar().arguments
        expected = [Argument('opt', {'spec':'[]','type':'dict','delim':';','expanded':True}), 
                    Argument('arg1', {'type':'str','spec':'<>','expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testInvalidArgumentString(self):
        class foobar(Macro):
            args = '[ %;opt ] < $+arg1 >'
        try: arg = foobar().arguments
        except ValueError: pass
        else: self.fail("Expected a ValueError")

    def testInvalidArgumentString2(self):
        class foobar(Macro):
            args = '[ %;opt ] < $*arg1 >'
        try: arg = foobar().arguments
        except ValueError: pass
        else: self.fail("Expected a ValueError")

    def testStringArgument(self):
        s = TeX('{foo {bar} one}')
        arg = s.getArgument(type='str')
        output = 'foo bar one'
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testIntegerArgument(self):
        s = TeX('{1{0}2}')
        arg = s.getArgument(type='int')
        output = 102
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testIntegerArgument(self):
        s = TeX('{ -1{0}2.67 }')
        arg = s.getArgument(type='float')
        output = -102.67
        assert (output - arg) < 0.000001, '"%s" != "%s"' % (arg, output)

    def testListArgument(self):
        s = TeX('{foo, {bar}, one}')
        arg = s.getArgument(type='list')
        output = ['foo','bar','one']
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testListArgument2(self):
        s = TeX('{foo; {bar}; one}')
        arg = s.getArgument(type='list', delim=';')
        output = ['foo','bar','one']
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testDictArgument(self):
        s = TeX('{one=1, two={2}, three=3}')
        arg = s.getArgument(type='dict')
        output = {'one':'1', 'two':'2', 'three':'3'}
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testDictArgument2(self):
        s = TeX('{one=1, two={\par}, three={$(x,y)$}, four=4}')
        arg = s.getArgument(type='dict')
        keys = arg.keys()
        keys.sort()
        expectkeys = ['four','one','three','two']
        assert keys == expectkeys, '"%s" != "%s"' % (keys, expectkeys)
        assert arg['one'] == '1'
        assert arg['four'] == '4'

    def testTokenArgument(self):
        s = TeX(r'\foo a ')
        arg = s.getArgument(type='Tok')
        assert arg == 'foo'
        arg = s.getArgument(type='Tok')
        assert arg == 'a'

    def testXTokenArgument(self):
        s = TeX(r'\newcommand{\foo}{\it}')
        [x for x in s]
        s.input(r'\foo a ')
        arg = s.getArgument(type='XTok')
        assert arg.nodeName == 'it', arg.nodeName
        arg = s.getArgument(type='XTok')
        assert arg == 'a', arg

    def testDimen(self):
        s = TeX(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.context['mycount'].value
        assert value == count(120), value
        value = s.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal dimension, this will only parse the `3`
        s.input(r'3.5pt')
        arg = s.getArgument(type='dimen')
        assert arg == dimen('3.0pt'), arg

        # Literal dimension
        s.input(r'{3.5pt}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen('3.5pt'), arg

        # Set by other dimension
        s.input(r'\mydimen')
        arg = s.getArgument(type='dimen')
        assert arg == dimen('12sp'), arg

        # Set by other dimension
        s.input(r'{\mydimen}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen('12sp'), arg

        # Multiply by other dimension
        s.input(r'{3.0\mydimen}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen('36sp'), arg

        # No number
        s.input('{a}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen(0), arg 
        
        # No number
        s.input('b')
        arg = s.getArgument(type='dimen')
        assert arg == dimen(0), arg 

        # Coerced dimen
        s.input('{\mycount}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen(120), arg

        # Coerced glue
        s.input('{\myglue}')
        arg = s.getArgument(type='dimen')
        assert arg == dimen(10), arg

    def testNumber(self):
        s = TeX(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.context['mycount'].value
        assert value == count(120), value
        value = s.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal number, this will only parse the `1`
        s.input('100')
        arg = s.getArgument(type='number')
        assert arg == count(1), arg

        # Literal number
        s.input('{100}')
        arg = s.getArgument(type='number')
        assert arg == count(100), arg

        # Set by other number
        s.input(r'\mycount')
        arg = s.getArgument(type='number')
        assert arg == count(120), arg

        # Set by other number
        s.input(r'{\mycount}')
        arg = s.getArgument(type='number')
        assert arg == count(120), arg

        # Multiply by other number
        s.input(r'{5\mycount}')
        arg = s.getArgument(type='number')
        assert arg == count(600), arg

        # No number
        s.input('{a}')
        arg = s.getArgument(type='number')
        assert arg == count(0), arg 
        
        # No number
        s.input('b')
        arg = s.getArgument(type='number')
        assert arg == count(0), arg 

        # Coerced dimen
        s.input('{\mydimen}')
        arg = s.getArgument(type='number')
        assert arg == count(12), arg

        # Coerced glue
        s.input('{\myglue}')
        arg = s.getArgument(type='number')
        assert arg == count(10), arg

    def testTeXDimen(self):
        s = TeX(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.context['mycount'].value
        assert value == count(120), value
        value = s.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal dimension
        s.input(r'3.5pt')
        arg = s.getArgument(type='Dimen')
        assert arg == dimen('3.5pt'), arg

        # Literal dimension, {...} aren't allowed
        s.input(r'{3.5pt}')
        arg = s.getArgument(type='Dimen')
        assert arg == dimen(0), arg

        # Set by other dimension
        s.input(r'\mydimen')
        arg = s.getArgument(type='Dimen')
        assert arg == dimen('12sp'), arg

        # Set by count
        s.input(r'\mycount')
        arg = s.getArgument(type='Dimen')
        assert arg == dimen('120sp'), arg

    def testListTypes(self):
        s = TeX(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        s.input('{1, \mycount, 3}')
        arg = s.getArgument(type='list', subtype='int')
        assert arg == [1, 120, 3], arg
    

if __name__ == '__main__':
    unittest.main()

