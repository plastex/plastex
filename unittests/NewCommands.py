#!/usr/bin/env python

import unittest, sys
from unittest import TestCase
from plasTeX import Environment
from plasTeX.TeX import TeX
from plasTeX.Context import Macro


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
        output = s.parse() 
        assert len(output) == 1, output
#       assert s.context['mycommand'].definition == '\it'
        assert type(output[0]) == type(s.context['it'])
        del s.context['mycommand']

    def testNewCommandWithArgs(self):
        s = TeX(r'\newcommand{\mycommand}[2]{#1:#2}\mycommand{foo}{bar}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
        assert len(output) == 1
#       assert s.context['mycommand'].definition == '#1:#2'
        assert output[0] == 'foo:bar'
        del s.context['mycommand']

    def testNewCommandWithOptional(self):
        s = TeX(r'\newcommand{\mycommand}[2][opt]{#1:#2}\mycommand{bar}\mycommand[foo]{bar}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
        assert len(output) == 1
#       assert s.context['mycommand'].definition == '#1:#2'
#       assert s.context['mycommand'].opt == 'opt', '"%s" != "opt"' % (s.context['mycommand'].opt)
        assert output[0] == 'opt:barfoo:bar'
        del s.context['mycommand']

    def testSimpleNewEnvironment(self):
        s = TeX(r'\newenvironment{myenv}{\it}{}\begin{myenv}hi\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
        assert len(output) == 1, output
#       assert s.context['myenv'].definition[0] == '\\it', '"%s" != "\\it"' % (s.context['myenv'].definition[0])
        assert type(output[0]) == type(s.context['it'])
        del s.context['myenv']

    def testSimpleNewEnvironmentWithArgs(self):
        s = TeX(r'\newenvironment{myenv}[2]{#1:#2}{}\begin{myenv}{foo}{bar}hi\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
        assert len(output) == 1, output
#       assert s.context['myenv'].definition[0] == '#1:#2'
        assert output[0] == 'foo:barhi'
        del s.context['myenv']

    def testSimpleNewEnvironmentWithOptional(self):
        s = TeX(r'\newenvironment{myenv}[2][opt]{#1:#2}{;}\begin{myenv}{foo}hi\end{myenv}\begin{myenv}[one]{blah}bye\end{myenv}')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
        assert len(output) == 1
#       assert s.context['myenv'].definition[0] == '#1:#2'
#       assert s.context['myenv'].definition[1] == ';'
#       assert s.context['myenv'].opt == 'opt'
        assert output[0] == 'opt:foohi;one:blahbye;', '"%s" != "%s"' % (output[0], 'opt:foohi;one:blahbye;')
        del s.context['myenv']

    def testNewEnvironment(self):
        s = TeX(r'\newenvironment{myenv}{\begin{description}}{\end{description}}before:\begin{myenv}hi\end{myenv}:after')
        for key, value in self.macros.items():
            s.context[key] = value
        output = s.parse() 
#       assert s.context['myenv'].definition[0] == r'\begin{description}'
#       assert s.context['myenv'].definition[1] == r'\end{description}'
#       assert s.context['myenv'].opt == None
        assert len(output) == 3, output
        assert type(output[1]) == type(s.context['description'])
        assert output[0] == 'before:'
        assert output[2] == ':after'
        del s.context['myenv']

    def testDef(self):
        s = TeX(r'\def\mymacro#1#2;#3\endmacro{this #1 is #2 my #3 command}\mymacro{one}x;y\endmacromorestuff')
        output = s.parse()
        assert len(output) == 1
        assert output[0] == 'this one is x my y commandmorestuff'
        del s.context['mymacro']

    def testDef2(self):
        s = TeX(r"\def\row#1{(#1_1,\ldots,#1_n)}\row{{x'}}")
        output = s.parse()
        assert len(output) == 7, output
        assert output[0] == "(x'"
        assert output[-1] == ')'
        del s.context['row']

    def testDef3(self):
        s = TeX(r'\def\foo#1#2{:#1:#2:}\foo x y')
        output = s.parse()
        assert len(output) == 1
        assert output[0] == ':x:y:'
        del s.context['foo']

    def testLet(self):
        s = TeX(r'\let\foo=\it\foo')
        output = s.parse()
        assert len(output) == 1
        assert type(output[0]) == type(s.context['it']) 
        del s.context['foo']

if __name__ == '__main__':
    unittest.main()

