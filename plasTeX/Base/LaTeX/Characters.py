"""
These macros are actually taken from the T1 font encoding package, but 
I figure that it wouldn't hurt to put them all in by default.

"""

from plasTeX import Command
from plasTeX.DOM import Node

class ding(Command):
    args = 'self'

    # Mapping from Zapf dingbats to unicode.
    # From https://unicode.org/Public/MAPPINGS/VENDORS/APPLE/DINGBATS.TXT
    values = {
        0x20: chr(0x0020),
        0x21: chr(0x2701),
        0x22: chr(0x2702),
        0x23: chr(0x2703),
        0x24: chr(0x2704),
        0x25: chr(0x260E),
        0x26: chr(0x2706),
        0x27: chr(0x2707),
        0x28: chr(0x2708),
        0x29: chr(0x2709),
        0x2A: chr(0x261B),
        0x2B: chr(0x261E),
        0x2C: chr(0x270C),
        0x2D: chr(0x270D),
        0x2E: chr(0x270E),
        0x2F: chr(0x270F),
        0x30: chr(0x2710),
        0x31: chr(0x2711),
        0x32: chr(0x2712),
        0x33: chr(0x2713),
        0x34: chr(0x2714),
        0x35: chr(0x2715),
        0x36: chr(0x2716),
        0x37: chr(0x2717),
        0x38: chr(0x2718),
        0x39: chr(0x2719),
        0x3A: chr(0x271A),
        0x3B: chr(0x271B),
        0x3C: chr(0x271C),
        0x3D: chr(0x271D),
        0x3E: chr(0x271E),
        0x3F: chr(0x271F),
        0x40: chr(0x2720),
        0x41: chr(0x2721),
        0x42: chr(0x2722),
        0x43: chr(0x2723),
        0x44: chr(0x2724),
        0x45: chr(0x2725),
        0x46: chr(0x2726),
        0x47: chr(0x2727),
        0x48: chr(0x2605),
        0x49: chr(0x2729),
        0x4A: chr(0x272A),
        0x4B: chr(0x272B),
        0x4C: chr(0x272C),
        0x4D: chr(0x272D),
        0x4E: chr(0x272E),
        0x4F: chr(0x272F),
        0x50: chr(0x2730),
        0x51: chr(0x2731),
        0x52: chr(0x2732),
        0x53: chr(0x2733),
        0x54: chr(0x2734),
        0x55: chr(0x2735),
        0x56: chr(0x2736),
        0x57: chr(0x2737),
        0x58: chr(0x2738),
        0x59: chr(0x2739),
        0x5A: chr(0x273A),
        0x5B: chr(0x273B),
        0x5C: chr(0x273C),
        0x5D: chr(0x273D),
        0x5E: chr(0x273E),
        0x5F: chr(0x273F),
        0x60: chr(0x2740),
        0x61: chr(0x2741),
        0x62: chr(0x2742),
        0x63: chr(0x2743),
        0x64: chr(0x2744),
        0x65: chr(0x2745),
        0x66: chr(0x2746),
        0x67: chr(0x2747),
        0x68: chr(0x2748),
        0x69: chr(0x2749),
        0x6A: chr(0x274A),
        0x6B: chr(0x274B),
        0x6C: chr(0x25CF),
        0x6D: chr(0x274D),
        0x6E: chr(0x25A0),
        0x6F: chr(0x274F),
        0x70: chr(0x2750),
        0x71: chr(0x2751),
        0x72: chr(0x2752),
        0x73: chr(0x25B2),
        0x74: chr(0x25BC),
        0x75: chr(0x25C6),
        0x76: chr(0x2756),
        0x77: chr(0x25D7),
        0x78: chr(0x2758),
        0x79: chr(0x2759),
        0x7A: chr(0x275A),
        0x7B: chr(0x275B),
        0x7C: chr(0x275C),
        0x7D: chr(0x275D),
        0x7E: chr(0x275E),
        0x80: chr(0x2768),
        0x81: chr(0x2769),
        0x82: chr(0x276A),
        0x83: chr(0x276B),
        0x84: chr(0x276C),
        0x85: chr(0x276D),
        0x86: chr(0x276E),
        0x87: chr(0x276F),
        0x88: chr(0x2770),
        0x89: chr(0x2771),
        0x8A: chr(0x2772),
        0x8B: chr(0x2773),
        0x8C: chr(0x2774),
        0x8D: chr(0x2775),
        0xA1: chr(0x2761),
        0xA2: chr(0x2762),
        0xA3: chr(0x2763),
        0xA4: chr(0x2764),
        0xA5: chr(0x2765),
        0xA6: chr(0x2766),
        0xA7: chr(0x2767),
        0xA8: chr(0x2663),
        0xA9: chr(0x2666),
        0xAA: chr(0x2665),
        0xAB: chr(0x2660),
        0xAC: chr(0x2460),
        0xAD: chr(0x2461),
        0xAE: chr(0x2462),
        0xAF: chr(0x2463),
        0xB0: chr(0x2464),
        0xB1: chr(0x2465),
        0xB2: chr(0x2466),
        0xB3: chr(0x2467),
        0xB4: chr(0x2468),
        0xB5: chr(0x2469),
        0xB6: chr(0x2776),
        0xB7: chr(0x2777),
        0xB8: chr(0x2778),
        0xB9: chr(0x2779),
        0xBA: chr(0x277A),
        0xBB: chr(0x277B),
        0xBC: chr(0x277C),
        0xBD: chr(0x277D),
        0xBE: chr(0x277E),
        0xBF: chr(0x277F),
        0xC0: chr(0x2780),
        0xC1: chr(0x2781),
        0xC2: chr(0x2782),
        0xC3: chr(0x2783),
        0xC4: chr(0x2784),
        0xC5: chr(0x2785),
        0xC6: chr(0x2786),
        0xC7: chr(0x2787),
        0xC8: chr(0x2788),
        0xC9: chr(0x2789),
        0xCA: chr(0x278A),
        0xCB: chr(0x278B),
        0xCC: chr(0x278C),
        0xCD: chr(0x278D),
        0xCE: chr(0x278E),
        0xCF: chr(0x278F),
        0xD0: chr(0x2790),
        0xD1: chr(0x2791),
        0xD2: chr(0x2792),
        0xD3: chr(0x2793),
        0xD4: chr(0x2794),
        0xD5: chr(0x2192),
        0xD6: chr(0x2194),
        0xD7: chr(0x2195),
        0xD8: chr(0x2798),
        0xD9: chr(0x2799),
        0xDA: chr(0x279A),
        0xDB: chr(0x279B),
        0xDC: chr(0x279C),
        0xDD: chr(0x279D),
        0xDE: chr(0x279E),
        0xDF: chr(0x279F),
        0xE0: chr(0x27A0),
        0xE1: chr(0x27A1),
        0xE2: chr(0x27A2),
        0xE3: chr(0x27A3),
        0xE4: chr(0x27A4),
        0xE5: chr(0x27A5),
        0xE6: chr(0x27A6),
        0xE7: chr(0x27A7),
        0xE8: chr(0x27A8),
        0xE9: chr(0x27A9),
        0xEA: chr(0x27AA),
        0xEB: chr(0x27AB),
        0xEC: chr(0x27AC),
        0xED: chr(0x27AD),
        0xEE: chr(0x27AE),
        0xEF: chr(0x27AF),
        0xF1: chr(0x27B1),
        0xF2: chr(0x27B2),
        0xF3: chr(0x27B3),
        0xF4: chr(0x27B4),
        0xF5: chr(0x27B5),
        0xF6: chr(0x27B6),
        0xF7: chr(0x27B7),
        0xF8: chr(0x27B8),
        0xF9: chr(0x27B9),
        0xFA: chr(0x27BA),
        0xFB: chr(0x27BB),
        0xFC: chr(0x27BC),
        0xFD: chr(0x27BD),
        0xFE: chr(0x27BE),
    }

    @property
    def str(self):
        code = int(self.textContent.strip())
        return type(self).values.get(code)

    @property
    def textContent(self):
        """ Get the text content of the current node """
        output = []
        for item in self:
            if item.nodeType == Node.TEXT_NODE:
                output.append(item)
            else:
                output.append(item.textContent)
        if self.ownerDocument is not None:
            return self.ownerDocument.createTextNode(''.join(output))
        else:
            return Text(''.join(output))

class textogonekcentered(Command):
    str = chr(731)

class textperthousand(Command):
    str = chr(8240)

class textpertenthousand(Command):
    str = chr(8241)

class textasciicircum(Command):
    str = '^'

class textasciitilde(Command):
    str = '~'

class textbackslash(Command):
    str = '\\'

class textbar(Command):
    str = '|'

class textbraceleft(Command):
    str = '{'

class textbraceright(Command):
    str = '}'

class textcompwordmark(Command): pass

class textdollar(Command):
    str = '$'

class textemdash(Command):
    str = chr(8212)

class textendash(Command):
    str = chr(8211)

class textexclamdown(Command):
    str = chr(161)

class textgreater(Command):
    str = '>'

class textless(Command):
    str = '<'

class textquestiondown(Command):
    str = chr(191)

class textquotedblleft(Command):
    str = chr(8220)

class textquotedblright(Command):
    str = chr(8221)

class textquotedbl(Command):
    str = '"'

class textquoteright(Command):
    str = chr(8217)

class textquoteleft(Command):
    str = chr(8216)

class textsection(Command):
    str = chr(167)

class textsterling(Command): pass

class textunderscore(Command):
    str = '_'

class textvisiblespace(Command):
    str = chr(160)

class texttrademark(Command):
   str = chr(8482)

class textregistered(Command):
   str = chr(174)

class textcopyright(Command):
   str = chr(169)

class AE(Command):
    str = chr(198)

class DH(Command):
    str = chr(272)

class DJ(Command):
    str = chr(272)

class L(Command):
    str = chr(321)

class NG(Command):
    str = chr(330)

class OE(Command):
    str = chr(338)

class O(Command):
    str = chr(216)

class SS(Command):
    str = chr(223)

class TH(Command):
    str = chr(222)

class ae(Command):
    str = chr(230)

class dh(Command): pass

class dj(Command):
    str = chr(273)

class guillmotleft(Command):
    str = chr(171)

class guillemotright(Command):
    str = chr(187)

class guilsinglleft(Command):
    str = chr(8249)

class guilsinglright(Command):
    str = chr(8250)

class i(Command):
    str = chr(305)

class j(Command): pass

class l(Command):
    str = chr(322)

class ng(Command):
    str = chr(331)

class oe(Command):
    str = chr(339)

class o(Command):
    str = chr(248)

class quotedblbase(Command):
    str = chr(8222)

class quotesinglbase(Command):
    str = chr(8218)

class ss(Command):
    str = 'SS'

class th(Command):
    str = chr(254)
