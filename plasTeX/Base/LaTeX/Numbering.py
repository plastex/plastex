#!/usr/bin/env python

"""
C.8.4 Numbering (p194)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger

class newcounter(Command):
    args = 'name:str [ within ]'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.newcounter(a['name'], a['within'])

class setcounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.counters[a['name']].setcounter(a['value'])

class addtocounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        self.ownerDocument.context.counters[a['name']].addtocounter(a['value'])

class value(Command):
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].arabic)

class arabic(Command):
    """ Return arabic representation """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].arabic)

class Roman(Command):
    """ Return uppercase roman representation """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        roman = ""
        n, number = divmod(int(self.ownerDocument.context.counters['name']), 1000)
        roman = "M"*n
        if number >= 900:
            roman = roman + "CM"
            number = number - 900
        while number >= 500:
            roman = roman + "D"
            number = number - 500
        if number >= 400:
            roman = roman + "CD"
            number = number - 400
        while number >= 100:
            roman = roman + "C"
            number = number - 100
        if number >= 90:
            roman = roman + "XC"
            number = number - 90
        while number >= 50:
            roman = roman + "L"
            number = number - 50
        if number >= 40:
            roman = roman + "XL"
            number = number - 40
        while number >= 10:
            roman = roman + "X"
            number = number - 10
        if number >= 9:
            roman = roman + "IX"
            number = number - 9
        while number >= 5:
            roman = roman + "V"
            number = number - 5
        if number >= 4:
            roman = roman + "IV"
            number = number - 4
        while number > 0:
            roman = roman + "I"
            number = number - 1
        return tex.textTokens(roman)

class roman(Roman):
    """ Return the lowercase roman representation """
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].roman)

class Alph(Command):
    """ Return the uppercase letter representation """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].Alph)

class alph(Alph):
    """ Return the lowercase letter representation """
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].alph)

class fnsymbol(Command):
    """ Return the symbol representation """
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(self.ownerDocument.context.counters[a['name']].fnsymbol)

class stepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return self.ownerDocument.context.counters[a['name']].stepcounter()

class refstepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        a = self.parse(tex)
        return self.ownerDocument.context.counters[a['name']].stepcounter()
