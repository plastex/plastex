#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro

class CategoryCodes(TestCase):

    def testLocalCatCodes(self):
        """ Make sure that category codes are local """
        class code(Macro):
            args = 'self:nox'
            def parse(self, tex):
                self.ownerDocument.context.catcode('#',11)
                self.ownerDocument.context.catcode('&',11)
                self.ownerDocument.context.catcode('^',11)
                self.ownerDocument.context.catcode('_',11)
                self.ownerDocument.context.catcode('$',11)
                return Macro.parse(self, tex)
        s = TeX()
        s.input('\code{this # is $ some & nasty _ text}&_2')
        s.ownerDocument.context['code'] = code
        tokens = [x for x in s]

        tok = type(tokens[0])
        cs = type(s.ownerDocument.createElement('code'))
        assert tok is cs, '"%s" != "%s"' % (tok, cs)

        assert not [x.catcode for x in tokens[0].attributes['self'] if x.catcode not in [10,11]], \
               'All codes should be 10 or 11: %s' % [x.code for x in tokens[0]]

        tok = type(tokens[-3])
        cs = type(s.ownerDocument.createElement('active::&'))
        assert tok is cs, '"%s" != "%s"' % (tok, cs)
    
#       tok = type(tokens[-2])
#       cs = type(s.ownerDocument.createElement('active::_'))
#       assert tok is cs, '"%s" != "%s"' % (tok, cs)

    def testLocalCatCodes2(self):
        class code(Macro):
            args = 'self'
        s = TeX()
        s.input("{\catcode`\#=11\catcode`\$=11\catcode`\&=11\catcode`\_=11{this # is $ some & nasty _ text}}&_2")
        s.ownerDocument.context['code'] = code
        tokens = [x for x in s]

        text = tokens[6:-5]
        assert not [x for x in text if x.catcode not in [10,11]], [x.catcode for x in text]

        tok = type(tokens[-3])
        tab = type(s.ownerDocument.createElement('active::&'))
        assert tok is tab, '"%s" != "%s"' % (tok, tab)
    
#       tok = type(tokens[-1])
#       tab = type(s.ownerDocument.createElement('active::_'))
#       assert tok is tab, '"%s" != "%s"' % (tok, tab)


if __name__ == '__main__':
    unittest.main()

