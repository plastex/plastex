#!/usr/bin/env python

from Tokenizer import Token
from plasTeX import Command, Environment


class alltt(Environment):

    def invoke(self, tex):
        esc = tex.context.categories[Token.CC_ESCAPE]
        begin = tex.context.categories[Token.CC_BGROUP]
        end = tex.context.categories[Token.CC_EGROUP]
        letters = tex.context.categories[Token.CC_LETTER]
        tex.context.setVerbatimCatcodes()
        for i in esc:
            tex.context.catcode(i, Token.CC_ESCAPE)
        for i in begin:
            tex.context.catcode(i, Token.CC_BGROUP)
        for i in end:
            tex.context.catcode(i, Token.CC_EGROUP)
        for i in letters:
            tex.context.catcode(i, Token.CC_LETTER)
        tex.context.catcode('$', Token.CC_MATHSHIFT)
        Environment.invoke(self, tex)

