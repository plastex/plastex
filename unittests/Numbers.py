#!/usr/bin/env python

import unittest, sys
from unittest import TestCase
from plasTeX.Tokenizer import *
from plasTeX.TeX import *

class Numbers(TestCase):

    def testReadDecimal(self):
        i = TeX(r'-1.0').readDecimal()
        assert i == -1, 'expected -1, but got %s' % i
        i = TeX(r'-11234.0').readDecimal()
        assert i == -11234, 'expected -11234, but got %s' % i
        i = TeX(r'0.0').readDecimal()
        assert i == 0, 'expected 0, but got %s' % i

    def testReadDimen(self):
        fuzz = 1e-3
        i = TeX(r'3 in').readDimen()
        assert i.inch - 3 < fuzz, i.inch
        i = TeX(r'29 pc').readDimen()
        assert i.pc - 29 < fuzz, i.pc 
        i = TeX(r'-.013837in').readDimen()
        assert i.inch - -0.013837 < fuzz, i.inch
        i = TeX(r'+ 42,1 dd').readDimen()
        assert i.dd - 42.1 < fuzz, i.dd
        i = TeX(r'0.mm').readDimen()
        assert i.mm - 0 < fuzz, i.mm
        i = TeX(r'123456789sp').readDimen()
        assert i.sp - 123456789 < fuzz, i.sp

    def testReadDimen2(self):
        # This is illegal
#       i = TeX(r"'.77pt").readDimen()
#       i = TeX(r'"Ccc').readDimen()
        i = TeX(r'-,sp').readDimen()
        assert i.sp == 0, i.sp

    def testUnitConversion(self):
        fuzz = 1e-3
        i = TeX(r'1 pc').readDimen()
        assert i.pt - 12 < fuzz, i.pt
        i = TeX(r'1 in').readDimen()
        assert i.pt - 72.27 < fuzz, i.pt
        i = TeX(r'72 bp').readDimen()
        assert i.inch - 1 < fuzz, i.inch
        i = TeX(r'2.54 cm').readDimen()
        assert i.inch - 1 < fuzz, i.inch
        i = TeX(r'10 mm').readDimen()
        assert i.cm - 1 < fuzz, i.cm
        i = TeX(r'1157 dd').readDimen()
        assert i.pt - 1238 < fuzz, i.pt
        i = TeX(r'1 cc').readDimen()
        assert i.dd - 12 < fuzz, i.dd
        i = TeX(r'65536 sp').readDimen()
        assert i.pt - 1 < fuzz, i.pt
       
    def testReadGlue(self):
        i = TeX(r'0pt plus 1fil').readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink is None, i.shrink

        i = TeX(r'0pt plus 1fill').readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink is None, i.shrink

        i = TeX(r'0pt plus 1fil minus 1 fil').readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink.fil == 1, i.shrink.fil 

        i = TeX(r'0pt plus -1fil').readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == -1, i.stretch.fil 
        assert i.shrink is None, i.shrink

    def testReadGlue2(self):
        i = TeX(r'6pt plus 2pt minus 2pt').readGlue()
        assert i.pt == 6, i.pt
        assert i.stretch.pt == 2, i.stretch.pt
        assert i.shrink.pt == 2, i.shrink.pt
        
        t = TeX(r'6pt plus 2pt minus 2pt 1.2pt plus -1.fil-1.234pt\foo')
        i = t.readGlue()
        j = t.readGlue()
        k = t.readGlue()

#       print i.source
        assert i.pt == 6, i.pt
        assert i.stretch.pt == 2, i.stretch.pt
        assert i.shrink.pt == 2, i.shrink.pt

#       print j.source
        assert j.pt == 1.2, i.pt
        assert j.stretch.fil == -1, j.stretch.fil
        assert j.shrink is None
        
#       print k.source
        assert k.pt == -1.234, k.pt
        assert k.stretch is None
        assert k.shrink is None

        tokens = [x for x in t.itertokens()]
        assert tokens == [EscapeSequence('foo')], tokens
        

if __name__ == '__main__':
    unittest.main()
