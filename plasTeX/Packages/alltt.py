#!/usr/bin/env python

from Tokenizer import Token
from plasTeX import Command, Environment


class alltt(Environment):

    def invoke(self, tex):
        tex.context.push(self)
        esc = tex.context.categories[Token.CC_ESCAPE]
        begin = tex.context.categories[Token.CC_BGROUP]
        end = tex.context.categories[Token.CC_EGROUP]
        tex.context.setVerbatimCatcodes()
        for i in esc:
            tex.context.catcode(i, Token.CC_ESCAPE)
        for i in begin:
            tex.context.catcode(i, Token.CC_BGROUP)
        for i in end:
            tex.context.catcode(i, Token.CC_EGROUP)
        Environment.invoke(self, tex)
        tex.context.pop(self)

