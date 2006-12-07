#!/usr/bin/env python

import unittest, sys
from unittest import TestCase
from plasTeX import Macro, Environment, Node, Command
from plasTeX.TeX import TeX
from plasTeX.Context import Context

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
        s = TeX()
        s.input(r'\newcommand\mycommand[2][optional]{\itshape{#1:#2}}\newcommand{ \foo }{{this is foo}}\mycommand[hi]{{\foo}!!!}')
        res = [x for x in s]
        text = [x for x in res if x.nodeType == Node.TEXT_NODE]
        expected = list('hi:this is foo!!!')
        assert text == expected, '%s != %s' % (text, expected)

    def testNewenvironment(self):
        s = TeX()
        s.input(r'\newenvironment{foo}{\begin{itemize}}{\end{itemize}}\begin{foo}\begin{foo}\item hi\end{foo}\end{foo}')
        res = [x for x in s]
        assert res[1].nodeName == 'bgroup'
        assert res[2].nodeName == 'itemize'
        assert res[3].nodeName == 'bgroup'
        assert res[4].nodeName == 'itemize'
        assert res[5].nodeName == 'item'
        assert res[6:8] == list('hi')
        assert res[8].nodeName == 'itemize'
        assert res[9].nodeName == 'egroup'
        assert res[10].nodeName == 'itemize'
        assert res[11].nodeName == 'egroup'

    def testReadDecimal(self):
        s = TeX()
        s.input(r'-1.0')
        i = s.readDecimal()
        assert i == -1, 'expected -1, but got %s' % i
        s = TeX()
        s.input(r'-11234.0')
        i = s.readDecimal()
        assert i == -11234, 'expected -11234, but got %s' % i
        s = TeX()
        s.input(r'0.0')
        i = s.readDecimal()
        assert i == 0, 'expected 0, but got %s' % i

    def testCatcode(self):
        s = TeX()
        s.input(r'\catcode`<=2')
        output = [x for x in s]
        assert '<' in s.ownerDocument.context.categories[2]

class NewCommands(TestCase):

    def setUp(self):
        self.macros = {}

        class it(Environment): pass

        class description(Environment): pass

        self.macros['it'] = it
        self.macros['description'] = description

    def testSimpleNewCommand(self):
        s = TeX()
        s.input(r'\newcommand\mycommand{\it}\mycommand')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        result = type(output[1])
        expected = type(s.ownerDocument.createElement('it'))
        assert result == expected, '"%s" != "%s"' % (result, expected)

    def testNewCommandWithArgs(self):
        s = TeX()
        s.input(r'\newcommand{\mycommand}[2]{#1:#2}\mycommand{foo}{bar}')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        assert s.ownerDocument.context['mycommand'].definition == list('#1:#2')
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('foo:bar'), text

    def testNewCommandWithOptional(self):
        s = TeX()
        s.input(r'\newcommand{\mycommand}[2][opt]{#1:#2}\mycommand{bar}\mycommand[foo]{bar}')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        assert s.ownerDocument.context['mycommand'].definition == list('#1:#2')
        assert s.ownerDocument.context['mycommand'].opt == list('opt'), '"%s" != "opt"' % (s.ownerDocument.context['mycommand'].opt)
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('opt:barfoo:bar'), text

    def testSimpleNewEnvironment(self):
        s = TeX()
        s.input(r'\newenvironment{myenv}{\it}{}\begin{myenv}hi\end{myenv}')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        assert type(output[2]) == s.ownerDocument.context['it']
        assert output[-3:-1] == ['h','i']

    def testSimpleNewEnvironmentWithArgs(self):
        s = TeX()
        s.input(r'\newenvironment{myenv}[2]{#1:#2}{}\begin{myenv}{foo}{bar}hi\end{myenv}')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        definition = s.ownerDocument.context['myenv'].definition
        enddefinition = s.ownerDocument.context['endmyenv'].definition
        assert definition == list('#1:#2'), definition
        assert enddefinition == [], enddefinition
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('foo:barhi'), text

    def testSimpleNewEnvironmentWithOptional(self):
        s = TeX()
        s.input(r'\newenvironment{myenv}[2][opt]{#1:#2}{;}\begin{myenv}{foo}hi\end{myenv}\begin{myenv}[one]{blah}bye\end{myenv}')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        definition = s.ownerDocument.context['myenv'].definition
        enddefinition = s.ownerDocument.context['endmyenv'].definition
        assert definition == list('#1:#2'), definition
        assert enddefinition == list(';'), enddefinition
        assert s.ownerDocument.context['myenv'].opt == list('opt')
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('opt:foohi;one:blahbye;'), text

    def testNewEnvironment(self):
        s = TeX()
        s.input(r'\newenvironment{myenv}{\begin{description}}{\end{description}}before:\begin{myenv}hi\end{myenv}:after')
        for key, value in self.macros.items():
            s.ownerDocument.context[key] = value
        output = [x for x in s]
        definition = s.ownerDocument.context['myenv'].definition
        enddefinition = s.ownerDocument.context['endmyenv'].definition
        assert definition == ['begin'] + list('{description}'), definition
        assert enddefinition == ['end'] + list('{description}'), enddefinition
        assert s.ownerDocument.context['myenv'].opt == None
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert type(output[9]) == s.ownerDocument.context['description']
        assert text == list('before:hi:after'), text

    def testDef(self):
        s = TeX()
        s.input(r'\def\mymacro#1#2;#3\endmacro{this #1 is #2 my #3 command}\mymacro{one}x;y\endmacro morestuff')
        output = [x for x in s]
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('this one is x my y commandmorestuff'), text

    def testDef2(self):
        s = TeX()
        s.input(r"\def\row#1{(#1_1,\ldots,#1_n)}\row{{x'}}")
        output = [x for x in s]
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list('(x\'_1,,x\'_n)'), text
        assert output[0].nodeName == 'def'
        assert output[6] == '_'
        assert output[9].nodeName == 'ldots'

    def testDef3(self):
        s = TeX()
        s.input(r'\def\foo#1#2{:#1:#2:}\foo x y')
        output = [x for x in s]
        text = [x for x in output if x.nodeType == Node.TEXT_NODE]
        assert text == list(':x:y:'), text

    def testLet(self):
        s = TeX()
        s.input(r'\let\foo=\it\foo')
        output = [x for x in s]
        assert type(output[1]) == s.ownerDocument.context['it'] 

        s = TeX()
        s.input(r'\let\bgroup={\bgroup')
        output = [x for x in s]
        assert output[1].source == '{', '"%s" != "%s"' % (output[1].source, '{')

    def testChardef(self):
        s = TeX()
        s.input(r'\chardef\foo=65\relax\foo')
        output = [x for x in s]
        assert output[-1].unicode == 'A', output


class Python(TestCase):

    def testStringCommand(self):
        class figurename(Command): unicode = 'Figure'
        s = TeX()
        s.input(r'\figurename')
        s.ownerDocument.context['figurename'] = figurename
        output = [x for x in s]
        assert output[0].unicode == 'Figure', output
       

if __name__ == '__main__':
    unittest.main()

