#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX.Context import Macro

class CategoryCodes(TestCase):

    def testLocalCatCodes(self):
        """ Make sure that category codes are local """
        class code(Macro):
            args = 'self'
            def parse(self, tex):
                tex.context.setCategoryCode('#',11)
                tex.context.setCategoryCode('&',11)
                tex.context.setCategoryCode('^',11)
                tex.context.setCategoryCode('_',11)
                tex.context.setCategoryCode('$',11)
                return Macro.parse(self, tex)
            def __repr__(self):
                return '<code>%s</code>' % list.__repr__(self)
        s = TeX('\code{this # is $ some & nasty _ text}&_2')
        s.context['code'] = code
        tokens = s.parse()

        assert len(tokens) == 3

        assert type(tokens[0]) is code, '"%s" != "%s"' % (type(tokens[0]), code)

        text = 'this # is $ some & nasty _ text'
        assert tokens[0][0] == text, '"%s" != "%s"' % (tokens[0][0], text)

        tok = type(tokens[1])
        tab = type(s.context['alignmenttab'])
        assert type(tok) is type(tab), '"%s" != "%s"' % (tok, tab)
    
        tok = type(tokens[2])
        tab = type(s.context['subscript'])
        assert type(tok) is type(tab), '"%s" != "%s"' % (tok, tab)

    def testLocalCatCodes2(self):
        class code(Macro):
            args = 'self'
        s = TeX("\code{\catcode`\#=11\catcode`\$=11\catcode`\&=11\catcode`\_=11this # is $ some & nasty _ text}&_2")
        s.context['code'] = code
        tokens = s.parse()

        assert len(tokens) == 3

        assert type(tokens[0]) is code, '"%s" != "%s"' % (type(tokens[0]), code)

        text = 'this # is $ some & nasty _ text'
        assert tokens[0][0] == text, '"%s" != "%s"' % (tokens[0][0], text)

        tok = type(tokens[1])
        tab = type(s.context['alignmenttab'])
        assert type(tok) is type(tab), '"%s" != "%s"' % (tok, tab)
    
        tok = type(tokens[2])
        tab = type(s.context['subscript'])
        assert type(tok) is type(tab), '"%s" != "%s"' % (tok, tab)


if __name__ == '__main__':
    unittest.main()

