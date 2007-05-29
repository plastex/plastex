#!/usr/bin/env python

import unittest, re
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Command, Environment

class Document(TestCase):

    def testParentage(self):
        class myenv(Environment):
            pass
        class foo(Command):
            args = 'self'
        s = TeX()
        s.ownerDocument.context.importMacros(locals())
        s.input(r'\begin{myenv}\foo{TEST}\end{myenv}')
        output = s.parse()

        myenv = output[0]
        assert myenv.nodeName == 'myenv', myenv.nodeName

        foo = output[0][0]
        assert foo.nodeName == 'foo', foo.nodeName

        children = output[0][0].childNodes
        fooself = output[0][0].attributes['self']
        assert children is fooself

        # Check parents
        assert fooself[0].parentNode is fooself, fooself[0].parentNode
        assert foo.parentNode is myenv, foo.parentNode
        assert myenv.parentNode is output, myenv.parentNode
        assert output.parentNode is None, output.parentNode

        # Check owner document
        assert fooself[0].ownerDocument is output
        assert foo.ownerDocument is output
        assert myenv.ownerDocument is output
        assert output.ownerDocument is output


if __name__ == '__main__':
    unittest.main()

