#!/usr/bin/env python

from plasTeX import Command
from plasTeX.Base.LaTeX import Accents

class textonequarter(Command):
    unicode = u'\u00BC'

class textonehalf(Command):
    unicode = u'\u00BD'

class textthreequarters(Command):
    unicode = u'\u00BE'

class textzerooldstyle(Command):
    unicode = '0'

class textoneoldstyle(Command):
    unicode = '1'

class texttwooldstyle(Command):
    unicode = '2'

class textthreeoldstyle(Command):
    unicode = '3'

class textfouroldstyle(Command):
    unicode = '4'

class textfiveoldstyle(Command):
    unicode = '5'

class textsixoldstyle(Command):
    unicode = '6'

class textsevenoldstyle(Command):
    unicode = '7'

class texteightoldstyle(Command):
    unicode = '8'

class textnineoldstyle(Command):
    unicode = '9'

class textflorin(Command):
    unicode = u'\u0192'

class textyen(Command):
    unicode = u'\u00a5'

class textwon(Command):
    unicode = u'\u20a9'

class textnaira(Command):
    unicode = u'\u20a6'

class textpeso(Command):
    unicode = u'\u20b1'

class textborn(Command):
    unicode = u'\u2605'

class textdied(Command):
    unicode = u'\u2020'

class textmarried(Command):
    unicode = u'\u26ad'

class textdivorced(Command):
    unicode = u'\u26ae'

class textcelsius(Command):
    unicode = u'\u00b0C'

class textopenbullet(Command):
    unicode = u'\u25e6'

class textdollaroldstyle(Command):
    unicode = '$'

class textsterling(Command):
    unicode = u'\u00a3'

class textlira(Command):
    unicode = u'\u20a4'

class textguarani(Command):
    unicode = u'\u20b2'

class texteuro(Command):
    unicode = u'\u20ac'

class textcentoldstyle(Command):
    unicode = u'\u00a2'

class textestimated(Command):
    unicode = u'\u212e'

class newtie(Accents.t):
    macroName = None

class capitaltie(Accents.t):
    macroName = None

class capitalacute(Accents.Acute):
    macroName = None

class capitaldieresis(Accents.Umlaut):
    macroName = None

class capitalbreve(Accents.Macron):
    macroName = None

class capitalnewtie(Accents.t):
    macroName = None

class capitalgrave(Accents.Grave):
    macroName = None

class capitaldotaccent(Accents.Dot):
    macroName = None

class capitalcedilla(Accents.c):
    macroName = None
