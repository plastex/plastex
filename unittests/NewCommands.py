#!/usr/bin/env python

import unittest, sys
from unittest import TestCase
from plasTeX import Macro, Environment
from plasTeX.TeX import TeX
from plasTeX.Context import Context
from plasTeX.Utils import isinternal

class ContextGenerated(TestCase):
    def testNewcommand(self):
        c = Context()
        c.newcommand('foo')
        c.newcommand('bar', 0, r'\it\bf')
        keys = c.keys()
        keys.sort()
        assert keys == ['bar','foo'], keys


class NC(TestCase):

    def testNewcommand(self):
        s = TeX(r'\newcommand\mycommand[2][optional]{\itshape{#1:#2}}\newcommand{ \foo }{{this is foo}}\mycommand[hi]{{\foo}!!!}')
        res = [x for x in s]
        text = [x for x in res if isinstance(x, basestring)]
        expected = list('hi:this is foo!!!')
        assert text == expected, '%s != %s' % (text, expected)

    def testNewenvironment(self):
        s = TeX(r'\newenvironment{foo}{\begin{list}}{\end{list}}\begin{foo}\begin{foo}\item hi\end{foo}\end{foo}')
        res = [x for x in s if not isinternal(x)]
        assert res[1].nodeName == 'list'
        assert res[2].nodeName == 'list'
        assert res[3].nodeName == 'item'
        assert res[4:6] == list('hi')
        assert res[6].nodeName == 'list'
        assert res[7].nodeName == 'list'

    def testReadDecimal(self):
        i = TeX(r'-1.0').readDecimal()
        assert i == -1, 'expected -1, but got %s' % i
        i = TeX(r'-11234.0').readDecimal()
        assert i == -11234, 'expected -11234, but got %s' % i
        i = TeX(r'0.0').readDecimal()
        assert i == 0, 'expected 0, but got %s' % i

    def testCatcode(self):
        s = TeX(r'\catcode`<=2')
        output = [x for x in s]
        assert '<' in s.context.categories[2]

class NewCommands(TestCase):

    def setUp(self):
        self.macros = {}

        class it(Environment):
            def __repr__(self):
                return '<it>%s</it>' % ''.join([str(x) for x in self])

        class description(Environment):
            def __repr__(self):
                return '<description>%s</description>' % ''.join([str(x) for x in self])

        self.macros['it'] = it
        self.macros['description'] = description

    def testSimpleNewCommand(self):
        s = TeX(r'\newcommand\mycommand{\it}\mycommand')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        result = type(output[1])
        expected = type(s.context['it'])
        assert result == expected, '"%s" != "%s"' % (result, expected)

    def testNewCommandWithArgs(self):
        s = TeX(r'\newcommand{\mycommand}[2]{#1:#2}\mycommand{foo}{bar}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        assert s.context['mycommand'].definition == list('#1:#2')
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('foo:bar'), text

    def testNewCommandWithOptional(self):
        s = TeX(r'\newcommand{\mycommand}[2][opt]{#1:#2}\mycommand{bar}\mycommand[foo]{bar}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        assert s.context['mycommand'].definition == list('#1:#2')
        assert s.context['mycommand'].opt == list('opt'), '"%s" != "opt"' % (s.context['mycommand'].opt)
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('opt:barfoo:bar'), text

    def testSimpleNewEnvironment(self):
        s = TeX(r'\newenvironment{myenv}{\it}{}\begin{myenv}hi\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        assert type(output[1]) == type(s.context['it'])
        assert output[-2:] == ['h','i']

    def testSimpleNewEnvironmentWithArgs(self):
        s = TeX(r'\newenvironment{myenv}[2]{#1:#2}{}\begin{myenv}{foo}{bar}hi\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        definition = s.context['myenv'].definition
        enddefinition = s.context['endmyenv'].definition
        assert definition == list('#1:#2'), definition
        assert enddefinition == [], enddefinition
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('foo:barhi'), text

    def testSimpleNewEnvironmentWithOptional(self):
        s = TeX(r'\newenvironment{myenv}[2][opt]{#1:#2}{;}\begin{myenv}{foo}hi\end{myenv}\begin{myenv}[one]{blah}bye\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        definition = s.context['myenv'].definition
        enddefinition = s.context['endmyenv'].definition
        assert definition == list('#1:#2'), definition
        assert enddefinition == list(';'), enddefinition
        assert s.context['myenv'].opt == list('opt')
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('opt:foohi;one:blahbye;'), text

    def testNewEnvironment(self):
        s = TeX(r'\newenvironment{myenv}{\begin{description}}{\end{description}}before:\begin{myenv}hi\end{myenv}:after')
        for key, value in self.macros.items():
            s.context[key] = value
        output = [x for x in s]
        definition = s.context['myenv'].definition
        enddefinition = s.context['endmyenv'].definition
        assert definition == ['begin'] + list('{description}'), definition
        assert enddefinition == ['end'] + list('{description}'), enddefinition
        assert s.context['myenv'].opt == None
        text = [x for x in output if isinstance(x, basestring)]
        assert type(output[8]) == type(s.context['description'])
        assert text == list('before:hi:after'), text

    def testDef(self):
        s = TeX(r'\def\mymacro#1#2;#3\endmacro{this #1 is #2 my #3 command}\mymacro{one}x;y\endmacro morestuff')
        output = [x for x in s]
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('this one is x my y commandmorestuff'), text

    def testDef2(self):
        s = TeX(r"\def\row#1{(#1_1,\ldots,#1_n)}\row{{x'}}")
        output = [x for x in s if not isinternal(x)]
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list('(x\',,x\')'), text
        assert output[0].nodeName == 'def'
        assert output[6].nodeName == 'subscript'
        assert output[8].nodeName == 'ldots'

    def testDef3(self):
        s = TeX(r'\def\foo#1#2{:#1:#2:}\foo x y')
        output = [x for x in s]
        text = [x for x in output if isinstance(x, basestring)]
        assert text == list(':x:y:'), text

    def testLet(self):
        s = TeX(r'\let\foo=\it\foo')
        output = [x for x in s]
        assert type(output[1]) == type(s.context['it']) 

        s = TeX(r'\let\bgroup={\bgroup')
        output = [x for x in s]
        assert repr(output[1]) == '{'

if __name__ == '__main__':
    unittest.main()

