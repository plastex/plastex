#!/usr/bin/env python

import unittest, sys
from unittest import TestCase
from plasTeX.Tokenizer import *
from plasTeX.TeX import *

class Numbers(TestCase):

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

    def testReadDimen(self):
        fuzz = 1e-3
        s = TeX()
        s.input(r'3 in')
        i = s.readDimen()
        assert i.inch - 3 < fuzz, i.inch
        s = TeX()
        s.input(r'29 pc')
        i = s.readDimen()
        assert i.pc - 29 < fuzz, i.pc 
        s = TeX()
        s.input(r'-.013837in')
        i = s.readDimen()
        assert i.inch - -0.013837 < fuzz, i.inch
        s = TeX()
        s.input(r'+ 42,1 dd')
        i = s.readDimen()
        assert i.dd - 42.1 < fuzz, i.dd
        s = TeX()
        s.input(r'0.mm')
        i = s.readDimen()
        assert i.mm - 0 < fuzz, i.mm
        s = TeX()
        s.input(r'123456789sp')
        i = s.readDimen()
        assert i.sp - 123456789 < fuzz, i.sp

    def testReadDimen2(self):
        # This is illegal
#       s = TeX()
#       s.input(r"'.77pt")
#       i = s.readDimen()
#       s = TeX()
#       s.input(r'"Ccc')
#       i = s.readDimen()
        s = TeX()
        s.input(r'-,sp')
        i = s.readDimen()
        assert i.sp == 0, i.sp

    def testUnitConversion(self):
        fuzz = 1e-3
        s = TeX()
        s.input(r'1 pc')
        i = s.readDimen()
        assert i.pt - 12 < fuzz, i.pt
        s = TeX()
        s.input(r'1 in')
        i = s.readDimen()
        assert i.pt - 72.27 < fuzz, i.pt
        s = TeX()
        s.input(r'72 bp')
        i = s.readDimen()
        assert i.inch - 1 < fuzz, i.inch
        s = TeX()
        s.input(r'2.54 cm')
        i = s.readDimen()
        assert i.inch - 1 < fuzz, i.inch
        s = TeX()
        s.input(r'10 mm')
        i = s.readDimen()
        assert i.cm - 1 < fuzz, i.cm
        s = TeX()
        s.input(r'1157 dd')
        i = s.readDimen()
        assert i.pt - 1238 < fuzz, i.pt
        s = TeX()
        s.input(r'1 cc')
        i = s.readDimen()
        assert i.dd - 12 < fuzz, i.dd
        s = TeX()
        s.input(r'65536 sp')
        i = s.readDimen()
        assert i.pt - 1 < fuzz, i.pt
       
    def testReadGlue(self):
        s = TeX()
        s.input(r'0pt plus 1fil')
        i = s.readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink is None, i.shrink

        s = TeX()
        s.input(r'0pt plus 1fill')
        i = s.readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink is None, i.shrink

        s = TeX()
        s.input(r'0pt plus 1fil minus 1 fil')
        i = s.readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == 1, i.stretch.fil 
        assert i.shrink.fil == 1, i.shrink.fil 

        s = TeX()
        s.input(r'0pt plus -1fil')
        i = s.readGlue()
        assert i.pt == 0, i.pt
        assert i.stretch.fil == -1, i.stretch.fil 
        assert i.shrink is None, i.shrink

    def testReadGlue2(self):
        s = TeX()
        s.input(r'6pt plus 2pt minus 2pt')
        i = s.readGlue()
        assert i.pt == 6, i.pt
        assert i.stretch.pt == 2, i.stretch.pt
        assert i.shrink.pt == 2, i.shrink.pt
        
        t = TeX()
        t.input(r'6pt plus 2pt minus 2pt 1.2pt plus -1.fil-1.234pt\foo')
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

class Parameters(TestCase):

    def testParameters(self):
        t = TeX()
        t.input(r'\newcount\foo\foo=\tolerance')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        tolerance = t.ownerDocument.context['tolerance'].value
        assert foo == tolerance, '"%s" != "%s"' % (foo, tolerance)

        t = TeX()
        t.input(r'\newcount\foo\foo=7\tolerance')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        tolerance = t.ownerDocument.context['tolerance'].value
        assert foo == (7*tolerance), '"%s" != "%s"' % (foo, 7*tolerance)

        t = TeX()
        t.input(r'\newcount\foo\foo=-3\tolerance')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        tolerance = t.ownerDocument.context['tolerance'].value
        assert foo == (-3*tolerance), '"%s" != "%s"' % (foo, -3*tolerance)

    def testDimenParameters(self):
        t = TeX()
        t.input(r'\newdimen\foo\foo=\hsize')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        hsize = t.ownerDocument.context['hsize'].value
        assert foo == hsize, '"%s" != "%s"' % (foo, hsize)
        
        t = TeX()
        t.input(r'\newdimen\foo\foo=7.6\hsize')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        hsize = t.ownerDocument.context['hsize'].value
        assert foo == (7.6*hsize), '"%s" != "%s"' % (foo, 7.6*hsize)
        
        t = TeX()
        t.input(r'\newdimen\foo\foo=-4\hsize')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        hsize = t.ownerDocument.context['hsize'].value
        assert foo == (-4*hsize), '"%s" != "%s"' % (foo, (-4*hsize))
        
    def testGlueParameters(self):
        t = TeX()
        t.input(r'\newskip\foo\foo=\baselineskip')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        baselineskip = t.ownerDocument.context['baselineskip'].value
        assert foo == baselineskip, '"%s" != "%s"' % (foo, baselineskip)
        
        t = TeX()
        t.input(r'\newskip\foo\foo=7.6\baselineskip')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        baselineskip = t.ownerDocument.context['baselineskip'].value
        assert foo == (7.6*baselineskip), '"%s" != "%s"' % (foo, 7.6*baselineskip)
        
        t = TeX()
        t.input(r'\newskip\foo\foo=-4\baselineskip')
        t.parse()
        foo = t.ownerDocument.context['foo'].value
        baselineskip = t.ownerDocument.context['baselineskip'].value
        assert foo == (-4*baselineskip), '"%s" != "%s"' % (foo, (-4*baselineskip))

if __name__ == '__main__':
    unittest.main()
