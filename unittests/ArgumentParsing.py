#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX import Macro, Argument
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
            args = '[ %;opt ] < "arg1" >'
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
        arg = s.getArgument(type='tok')
        assert arg == 'foo'
        arg = s.getArgument(type='tok')
        assert arg == 'a'

    def testXTokenArgument(self):
        s = TeX(r'\newcommand{\foo}{\it}')
        [x for x in s]
        s.input(r'\foo a ')
        arg = s.getArgument(type='xtok')
        assert arg.nodeName == 'it', arg.nodeName
        arg = s.getArgument(type='xtok')
        assert arg == 'a', arg

if __name__ == '__main__':
    unittest.main()

