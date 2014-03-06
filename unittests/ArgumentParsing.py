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
        expected = [Argument('arg1', 0, {'expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString2(self):
        class foobar(Macro):
            args = '* [ opt ] arg1'
        arg = foobar().arguments
        expected = [Argument('*modifier*', 0, {'spec':'*'}),
                    Argument('opt', 1, {'spec':'[]','expanded':True}), 
                    Argument('arg1', 2, {'expanded':True})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString3(self):
        class foobar(Macro):
            args = '[ opt:dict ] arg1:list'
        arg = foobar().arguments
        expected = [Argument('opt', 0, {'spec':'[]','type':'dict','expanded':True,'delim':None}), 
                    Argument('arg1', 1, {'type':'list','expanded':True,'delim':None})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString4(self):
        class foobar(Macro):
            args = '[ opt:dict(;) ] arg1:list'
        arg = foobar().arguments
        expected = [Argument('opt', 0, {'spec':'[]','type':'dict','delim':';','expanded':True}), 
                    Argument('arg1', 1, {'type':'list','expanded':True,'delim':None})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def testArgumentString5(self):
        class foobar(Macro):
            args = '[ opt:dict(;) ] < arg1:str >'
        arg = foobar().arguments
        expected = [Argument('opt', 0, {'spec':'[]','type':'dict','delim':';','expanded':True}), 
                    Argument('arg1', 1, {'type':'str','spec':'<>','expanded':True, 'delim':None})]
        assert arg == expected, '"%s" != "%s"' % (arg, expected)
    
    def _testInvalidArgumentString(self):
        class foobar(Macro):
            args = '[ opt:dict(;) ] < arg1:str(+) >'
        try: arg = foobar().arguments
        except ValueError: pass
        else: self.fail("Expected a ValueError")

    def _testInvalidArgumentString2(self):
        class foobar(Macro):
            args = '[ opt:dict(;) ] < arg1:str(*) >'
        try: arg = foobar().arguments
        except ValueError: pass
        else: self.fail("Expected a ValueError")

    def testStringArgument(self):
        s = TeX()
        s.input('{foo {bar} one}')
        arg = s.readArgument(type='str')
        output = 'foo bar one'
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testIntegerArgument(self):
        s = TeX()
        s.input('{1{0}2}')
        arg = s.readArgument(type='int')
        output = 102
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testIntegerArgument(self):
        s = TeX()
        s.input('{ -1{0}2.67 }')
        arg = s.readArgument(type='float')
        output = -102.67
        assert (output - arg) < 0.000001, '"%s" != "%s"' % (arg, output)

    def testListArgument(self):
        s = TeX()
        s.input('{foo, {bar}, one}')
        arg = s.readArgument(type='list')
        output = ['foo','bar','one']
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testListArgument2(self):
        s = TeX()
        s.input('{foo; {bar}; one}')
        arg = s.readArgument(type='list', delim=';')
        output = ['foo','bar','one']
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testDictArgument(self):
        s = TeX()
        s.input('{one=1, two={2}, three=3}')
        arg = s.readArgument(type='dict')
        output = {'one':'1', 'two':'2', 'three':'3'}
        assert arg == output, '"%s" != "%s"' % (arg, output)

    def testDictArgument2(self):
        s = TeX()
        s.input('{one=1, two={\par}, three={$(x,y)$}, four=4}')
        arg = s.readArgument(type='dict')
        keys = arg.keys()
        keys.sort()
        expectkeys = ['four','one','three','two']
        assert keys == expectkeys, '"%s" != "%s"' % (keys, expectkeys)
        assert arg['one'] == '1'
        assert arg['four'] == '4'

    def testTokenArgument(self):
        s = TeX()
        s.input(r'\foo a ')
        arg = s.readArgument(type='Tok')
        assert arg == 'foo'
        arg = s.readArgument(type='Tok')
        assert arg == 'a'

    def testXTokenArgument(self):
        s = TeX()
        s.input(r'\newcommand{\foo}{\it}')
        [x for x in s]
        s.input(r'\foo a ')
        arg = s.readArgument(type='XTok')
        assert arg.nodeName == 'it', arg.nodeName
        arg = s.readArgument(type='XTok')
        assert arg == 'a', arg

    def testDimen(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.ownerDocument.context['mycount'].value
        assert value == count(120), value
        value = s.ownerDocument.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.ownerDocument.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal dimension, this will only parse the `3`
        s.input(r'3.5pt')
        arg = s.readArgument(type='dimen')
        assert arg == dimen('3.0pt'), arg

        # Literal dimension
        s.input(r'{3.5pt}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen('3.5pt'), arg

        # Set by other dimension
        s.input(r'\mydimen')
        arg = s.readArgument(type='dimen')
        assert arg == dimen('12sp'), arg

        # Set by other dimension
        s.input(r'{\mydimen}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen('12sp'), arg

        # Multiply by other dimension
        s.input(r'{3.0\mydimen}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen('36sp'), arg

        # No number
        s.input('{a}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen(0), arg 
        
        # No number
        s.input('b')
        arg = s.readArgument(type='dimen')
        assert arg == dimen(0), arg 

        # Coerced dimen
        s.input('{\mycount}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen(120), arg

        # Coerced glue
        s.input('{\myglue}')
        arg = s.readArgument(type='dimen')
        assert arg == dimen(10), arg

        assert ParameterCommand._enablelevel == 0

    def testTeXDimen(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.ownerDocument.context['mycount'].value
        assert value == count(120), value
        value = s.ownerDocument.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.ownerDocument.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal number
        s.input('100pt')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('100pt'), arg

        # Set by other dimen
        s.input('\mydimen')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('12sp'), arg

        # Multiply by other dimen
        s.input('3\mydimen')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('36sp'), arg

        # No number
        s.input('{0}')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen(0), arg

        assert ParameterCommand._enablelevel == 0

    def testNumber(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.ownerDocument.context['mycount'].value
        assert value == count(120), value
        value = s.ownerDocument.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.ownerDocument.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal number, this will only parse the `1`
        s.input('100')
        arg = s.readArgument(type='number')
        assert arg == count(1), arg

        # Literal number
        s.input('{100}')
        arg = s.readArgument(type='number')
        assert arg == count(100), arg

        # Set by other number
        s.input(r'\mycount')
        arg = s.readArgument(type='number')
        assert arg == count(120), arg

        # Set by other number
        s.input(r'{\mycount}')
        arg = s.readArgument(type='number')
        assert arg == count(120), arg

        # Multiply by other number
        s.input(r'{5\mycount}')
        arg = s.readArgument(type='number')
        assert arg == count(600), arg

        # No number
        s.input('{a}')
        arg = s.readArgument(type='number')
        assert arg == count(0), arg 
        
        # No number
        s.input('b')
        arg = s.readArgument(type='number')
        assert arg == count(0), arg 

        # Coerced dimen
        s.input('{\mydimen}')
        arg = s.readArgument(type='number')
        assert arg == count(12), arg

        # Coerced glue
        s.input('{\myglue}')
        arg = s.readArgument(type='number')
        assert arg == count(10), arg

        assert ParameterCommand._enablelevel == 0

    def testTeXDimen(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.ownerDocument.context['mycount'].value
        assert value == count(120), value
        value = s.ownerDocument.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.ownerDocument.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal dimension
        s.input(r'3.5pt')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('3.5pt'), arg

        # Literal dimension, {...} aren't allowed
        s.input(r'{3.5pt}')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen(0), arg

        # Set by other dimension
        s.input(r'\mydimen')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('12sp'), arg

        # Set by count
        s.input(r'\mycount')
        arg = s.readArgument(type='Dimen')
        assert arg == dimen('120sp'), arg

        assert ParameterCommand._enablelevel == 0

    def testTeXNumber(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        value = s.ownerDocument.context['mycount'].value
        assert value == count(120), value
        value = s.ownerDocument.context['mydimen'].value
        assert value == dimen('12sp'), value
        value = s.ownerDocument.context['myglue'].value
        assert value == glue('10sp', plus='1pt', minus='2pt'), value

        # Literal number
        s.input('100')
        arg = s.readArgument(type='Number')
        assert arg == count('100'), arg

        # Set by other dimen
        s.input('\mycount')
        arg = s.readArgument(type='Number')
        assert arg == count('120'), arg

        # Multiply by other dimen
        s.input('3\mycount')
        arg = s.readArgument(type='Number')
        assert arg == count('360'), arg

        # No number
        s.input('{0}')
        arg = s.readArgument(type='Number')
        assert arg == count(0), arg

        assert ParameterCommand._enablelevel == 0

    def testListTypes(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        s.input('{1, \mycount, 3}')
        arg = s.readArgument(type='list', subtype='int')
        assert arg == [1, 120, 3], arg
    
    def testDictTypes(self):
        s = TeX()
        s.input(r'''\newcount\mycount\mycount=120
                    \newdimen\mydimen\mydimen=12sp
                    \newskip\myglue\myglue=10sp plus1pt minus2pt''')
        s.parse()

        s.input('{one=1, two={\mycount} , three={3}}')
        arg = s.readArgument(type='dict', expanded=True)
        keys = arg.keys()
        keys.sort()
        assert keys == ['one', 'three', 'two']


if __name__ == '__main__':
    unittest.main()

