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
                tex.context.catcode('#',11)
                tex.context.catcode('&',11)
                tex.context.catcode('^',11)
                tex.context.catcode('_',11)
                tex.context.catcode('$',11)
                return Macro.parse(self, tex)
            def __repr__(self):
                return '<code>%s</code>' % Macro.__repr__(self)
        s = TeX('\code{this # is $ some & nasty _ text}&_2')
        s.context['code'] = code
        tokens = [x for x in s]

        tok = type(tokens[0])
        cs = type(s.context['code'])
        assert tok is cs, '"%s" != "%s"' % (tok, cs)

        assert not [x.catcode for x in tokens[0].attributes['self'] if x.catcode not in [10,11]], \
               'All codes should be 10 or 11: %s' % [x.code for x in tokens[0]]

        tok = type(tokens[-2])
        cs = type(s.context['alignmenttab'])
        assert tok is cs, '"%s" != "%s"' % (tok, cs)
    
        tok = type(tokens[-1])
        cs = type(s.context['subscript'])
        assert tok is cs, '"%s" != "%s"' % (tok, cs)

    def testLocalCatCodes2(self):
        class code(Macro):
            args = 'self'
            def __repr__(self):
                return '<code>%s</code>' % list.__repr__(self)
        s = TeX("{\catcode`\#=11\catcode`\$=11\catcode`\&=11\catcode`\_=11{this # is $ some & nasty _ text}}&_2")
        s.context['code'] = code
        tokens = [x for x in s]

        text = tokens[6:-5]
        assert not [x for x in text if x.catcode not in [10,11]], [x.catcode for x in text]

        tok = type(tokens[-2])
        tab = type(s.context['alignmenttab'])
        assert tok is tab, '"%s" != "%s"' % (tok, tab)
    
        tok = type(tokens[-1])
        tab = type(s.context['subscript'])
        assert tok is tab, '"%s" != "%s"' % (tok, tab)


if __name__ == '__main__':
    unittest.main()

