#!/usr/bin/env python

"""
These macros are actually taken from the T1 font encoding package, but 
I figure that it wouldn't hurt to put them all in by default.

"""

from plasTeX import Command

class ding(Command):
    args = 'self'
    values = {}
    @property
    def unicode(self):
        if int(self.textContent.strip()) in type(self).values:
            return type(self).values[int(self.textContent)]

class textogonekcentered(Command):
    unicode = unichr(731)

class textperthousand(Command):
    unicode = unichr(8240)

class textpertenthousand(Command):
    unicode = unichr(8241)

class textasciicircum(Command):
    unicode = '^'

class textasciitilde(Command):
    unicode = '~'

class textbackslash(Command):
    unicode = '\\'

class textbar(Command):
    unicode = '|'

class textbraceleft(Command):
    unicode = '{'

class textbraceright(Command):
    unicode = '}'

class textcompwordmark(Command): pass

class textdollar(Command):
    unicode = '$'

class textemdash(Command):
    unicode = unichr(8212)

class textendash(Command):
    unicode = unichr(8211)

class textexclamdown(Command):
    unicode = unichr(161)

class textgreater(Command):
    unicode = '>'

class textless(Command):
    unicode = '<'

class textquestiondown(Command):
    unicode = unichr(191)

class textquotedblleft(Command):
    unicode = unichr(8220)

class textquotedblright(Command):
    unicode = unichr(8221)

class textquotedbl(Command):
    unicode = '"'

class textquoteright(Command):
    unicode = unichr(8217)

class textquoteleft(Command):
    unicode = unichr(8216)

class textsection(Command):
    unicode = unichr(167)

class textsterling(Command): pass

class textunderscore(Command):
    unicode = '_'

class textvisiblespace(Command):
    unicode = unichr(160)

class AE(Command):
    unicode = unichr(198)

class DH(Command):
    unicode = unichr(272)

class DJ(Command):
    unicode = unichr(272)

class L(Command):
    unicode = unichr(321)

class NG(Command):
    unicode = unichr(330)

class OE(Command):
    unicode = unichr(338)

class O(Command):
    unicode = unichr(216)

class SS(Command):
    unicode = unichr(223)

class TH(Command):
    unicode = unichr(222)

class ae(Command):
    unicode = unichr(230)

class dh(Command): pass

class dj(Command):
    unicode = unichr(273)

class guillmotleft(Command):
    unicode = unichr(171)

class guillemotright(Command):
    unicode = unichr(187)

class guilsinglleft(Command):
    unicode = unichr(8249)

class guilsinglright(Command):
    unicode = unichr(8250)

class i(Command):
    unicode = unichr(305)

class j(Command): pass

class l(Command):
    unicode = unichr(322)

class ng(Command):
    unicode = unichr(331)

class oe(Command):
    unicode = unichr(339)

class o(Command):
    unicode = unichr(248)

class quotedblbase(Command):
    unicode = unichr(8222)

class quotesinglbase(Command):
    unicode = unichr(8218)

class ss(Command):
    unicode = 'SS'

class th(Command):
    unicode = unichr(254)
