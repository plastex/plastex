#!/usr/bin/env python

"""
C.8.4 Numbering (p194)

"""

from plasTeX.Tokenizer import Other
from plasTeX import Command, Environment
from plasTeX.Logging import getLogger

class newcounter(Command):
    args = 'name:str [ within ]'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.counters.new(a['name'], resetby=a['within'])

class setcounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.counters[a['name']] = a['value']

class addtocounter(Command):
    args = 'name:str value:int'
    def invoke(self, tex):
        a = self.parse(tex)
        tex.context.counters[a['name']] += a['value']

class value(Command):
    args = 'name:str'
    def invoke(self, tex):
        return [Other(tex.context.counters[self.parse(tex)['name']])]

class arabic(Command):
    """ Return arabic representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other(tex.context.counters[self.parse(tex)['name']])]

class Roman(Command):
    """ Return uppercase roman representation """
    args = 'name:str'
    def invoke(self, tex):
        roman = ""
        n, number = divmod(tex.context.counters[self.parse(tex)['name']], 1000)
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
        return [Other(roman)]

class roman(Roman):
    """ Return the lowercase roman representation """
    def invoke(self, tex):
        return [Other(x.lower()) for x in Roman.invoke()]

class Alph(Command):
    """ Return the uppercase letter representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other(tex.context.counters[self.parse(tex)['name']]-1).upper()]

class alph(Alph):
    """ Return the lowercase letter representation """
    def invoke(self, tex):
        return [Other(x.lower()) for x in Alph.invoke()]

class fnsymbol(Command):
    """ Return the symbol representation """
    args = 'name:str'
    def invoke(self, tex):
        return [Other('*' * self.value)]

class stepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        tex.context.counters.stepcounter(self.parse(text)['name'])

class refstepcounter(Command):
    args = 'name:str'
    def invoke(self, tex):
        tex.context.counters.stepcounter(self.parse(text)['name'])
