#!/usr/bin/env python

import unittest
from unittest import TestCase
from plasTeX import Macro
from plasTeX.TeX import *
from plasTeX.Tokenizer import *

class Tokenizing(TestCase):

    def testTokens(self):
        tokens = [x for x in TeX('{\hskip 36 pt}').itertokens()]
        expected = [BeginGroup('{'), 
                    EscapeSequence('hskip'), 
                    Other('3'),
                    Other('6'),
                    Space(' '),
                    Letter('p'), 
                    Letter('t'), 
                    EndGroup('}')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

    def testComment(self):
        tokens = [x for x in TeX('line % comment').itertokens()]
        expected = [Letter('l'), 
                    Letter('i'), 
                    Letter('n'), 
                    Letter('e'), 
                    Space(' ')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

    def testSymbols(self):
        tokens = [x for x in TeX('\\ { } $ & # ^ _ ~ %').itertokens()]
        expected = [EscapeSequence(' '),
                    BeginGroup('{'), Space(' '), 
                    EndGroup('}'), Space(' '), 
                    MathShift('$'), Space(' '), 
                    Alignment('&'), Space(' '), 
                    Parameter('#'), Space(' '), 
                    Superscript('^'), Space(' '), 
                    Subscript('_'), Space(' '), 
                    EscapeSequence('active::~'), Space(' ')]
        assert tokens == expected, '%s != %s' % (tokens, expected)
        
        tokens = [x for x in TeX(r'\\ \{ \} \$ \& \# \^ \_ \~ \%').itertokens()]
        expected = [EscapeSequence('\\'), Space(' '),
                    EscapeSequence('{'), Space(' '),
                    EscapeSequence('}'), Space(' '),
                    EscapeSequence('$'), Space(' '),
                    EscapeSequence('&'), Space(' '),
                    EscapeSequence('#'), Space(' '),
                    EscapeSequence('^'), Space(' '),
                    EscapeSequence('_'), Space(' '),
                    EscapeSequence('~'), Space(' '),
                    EscapeSequence('%')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

    def testDoubleSuper(self):
        tokens = [x for x in TeX('^^I ^^A ^^@ ^^M').itertokens()]
        expected = [Other('\x01'), Space(' ')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

    def testParagraph(self):
        tokens = [x for x in TeX('1\n   2\n   \n   3\n').itertokens()]
        expected = [Other('1'), Space(' '), 
                    Other('2'), Space(' '), 
                    EscapeSequence('par'), 
                    Other('3'), Space(' ')]
        assert tokens == expected, '%s != %s' % (tokens, expected)
         
    def testExercises(self):
        """ Exercises in the TeX book """
        # 8.4
        tokens = [x for x in TeX(r' $x^2$~  \TeX  ^^C').itertokens()]
        expected = [MathShift('$'), 
                    Letter('x'), 
                    Superscript('^'), 
                    Other('2'), 
                    MathShift('$'), 
                    EscapeSequence('active::~'), 
                    Space(' '), 
                    EscapeSequence('TeX'), 
                    Other('\x03')]
        assert tokens == expected, '%s != %s' % (tokens, expected)
        
        # 8.5
        tokens = [x for x in TeX('Hi!\n\n\n').itertokens()]
        expected = [Letter('H'), 
                    Letter('i'), 
                    Other('!'), 
                    Space(' '), 
                    EscapeSequence('par')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

        # 8.6
        tokens = [x for x in TeX(r'^^B^^BM^^A^^B^^C^^M^^@\M ').itertokens()]
        expected = [Other('\x02'), 
                    Other('\x02'), 
                    Letter('M'), 
                    Other('\x01'), 
                    Other('\x02'), 
                    Other('\x03'), 
                    Space(' '), 
                    EscapeSequence('M')]
        assert tokens == expected, '%s != %s' % (tokens, expected)

    def testParameters(self):
        tokens = [x for x in TeX(r'\def\foo#1[#2]{hi}').itertokens()]

if __name__ == '__main__':
    unittest.main()

