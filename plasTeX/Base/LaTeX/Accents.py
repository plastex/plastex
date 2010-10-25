#!/usr/bin/env python

"""
C.3.4 Accents and Special Symbols (p173)

"""

from plasTeX import Command, Environment
from plasTeX.Logging import getLogger
from plasTeX.DOM import Node, Text

#
# Table 3.1: Accents
#

class Accent(Command):
    args = 'self'
    chars = {}

    @property
    def unicode(self):
        return type(self).chars.get(self.textContent.strip(), None)

    @property    
    def textContent(self):
        """
        We need a customized textContent that doesn't look up 
        textContent recursively.
        
        """
        output = []
        for item in self:
            if item.nodeType == Node.TEXT_NODE:
                output.append(item)
            elif getattr(item, 'unicode', None) is not None:
                output.append(item.unicode)
            else:
                output.append(item.textContent)
        if self.ownerDocument is not None:
            return self.ownerDocument.createTextNode(u''.join(output))
        else:
            return Text(u''.join(output))        


class Grave(Accent):
    macroName = '`'
    chars = {
        'A': unichr(192),
        'E': unichr(200),
        'I': unichr(204),
        'O': unichr(210),
        'U': unichr(217),
        'a': unichr(224),
        'e': unichr(232),
        'i': unichr(236),
        'o': unichr(242),
        'u': unichr(249),
        'N': unichr(504),
        'n': unichr(505),
    }

class Acute(Accent):
    macroName = "'"
    chars = {
        'A': unichr(193),
        'E': unichr(201),
        'I': unichr(205),
        'O': unichr(211),
        'U': unichr(218),
        'Y': unichr(221),
        'a': unichr(225),
        'e': unichr(233),
        'i': unichr(237),
        'o': unichr(243),
        'u': unichr(250),
        'y': unichr(253),
        'C': unichr(262),
        'c': unichr(263),
        'L': unichr(313),
        'l': unichr(314),
        'N': unichr(323),
        'n': unichr(324),
        'R': unichr(340),
        'r': unichr(341),
        'S': unichr(346),
        's': unichr(347),
        'Z': unichr(377),
        'z': unichr(378),
        'G': unichr(500),
        'g': unichr(501),
    }

class Circumflex(Accent):
    macroName = '^'
    chars = {
        'A': unichr(194),
        'E': unichr(202),
        'I': unichr(206),
        'O': unichr(212),
        'U': unichr(219),
        'a': unichr(226),
        'e': unichr(234),
        'i': unichr(238),
        'o': unichr(244),
        'u': unichr(251),
        'C': unichr(264),
        'c': unichr(265),
        'G': unichr(284),
        'g': unichr(285),
        'H': unichr(292),
        'h': unichr(293),
        'J': unichr(308),
        'j': unichr(309),
        'S': unichr(348),
        's': unichr(349),
        'W': unichr(372),
        'w': unichr(373),
        'Y': unichr(374),
        'y': unichr(375),
        '': '^',
    }

class Umlaut(Accent):
    macroName = '"'
    chars = {
        'A': unichr(196),
        'E': unichr(203),
        'I': unichr(207),
        'O': unichr(214),
        'U': unichr(220),
        'a': unichr(228),
        'e': unichr(235),
        'i': unichr(239),
        'o': unichr(246),
        'u': unichr(252),
        'y': unichr(255),
        'Y': unichr(376),
    }

class Tilde(Accent):
    macroName = '~'
    chars = {
        'A': unichr(195),
        'N': unichr(209),
        'O': unichr(213),
        'a': unichr(227),
        'n': unichr(241),
        'o': unichr(245),
        'I': unichr(296),
        'i': unichr(297),
        'U': unichr(360),
        'u': unichr(361),
    }

class Macron(Accent):
    macroName = '='
    chars = {
        'A': unichr(256),
        'a': unichr(257),
        'E': unichr(274),
        'e': unichr(275),
        'I': unichr(298),
        'i': unichr(299),
        'O': unichr(332),
        'o': unichr(333),
        'U': unichr(362),
        'u': unichr(363),
        'Y': unichr(562),
        'y': unichr(563),
    }

class Dot(Accent):
    macroName = '.'
    chars = {
        'C': unichr(266),
        'c': unichr(267),
        'E': unichr(278),
        'e': unichr(279),
        'G': unichr(288),
        'g': unichr(289),
        'I': unichr(304),
        'Z': unichr(379),
        'z': unichr(380),
        'A': unichr(550),
        'a': unichr(551),
        'O': unichr(558),
        'o': unichr(559),
        'B': unichr(7682),
        'b': unichr(7683),
        'D': unichr(7690),
        'd': unichr(7691),
        'F': unichr(7710),
        'f': unichr(7711),
        'H': unichr(7714),
        'h': unichr(7715),
        'M': unichr(7744),
        'm': unichr(7745),
        'N': unichr(7748),
        'n': unichr(7749),
        'P': unichr(7766),
        'p': unichr(7767),
        'R': unichr(7768),
        'r': unichr(7769),
        'S': unichr(7776),
        's': unichr(7777),
        'T': unichr(7786),
        't': unichr(7787),
        'W': unichr(7814),
        'w': unichr(7815),
        'X': unichr(7818),
        'x': unichr(7819),
        'Y': unichr(7822),
        'y': unichr(7823),
    }

class u(Accent):
    chars = {
        'A': unichr(258),
        'a': unichr(259),
        'E': unichr(276),
        'e': unichr(277),
        'G': unichr(286),
        'g': unichr(287),
        'I': unichr(300),
        'i': unichr(301),
        'O': unichr(334),
        'o': unichr(335),
        'U': unichr(364),
        'u': unichr(365),
    }

class v(Accent):
    chars = {
        'C': unichr(268),
        'c': unichr(269),
        'D': unichr(270),
        'd': unichr(271),
        'E': unichr(282),
        'e': unichr(283),
        'L': unichr(317),
        'l': unichr(318),
        'N': unichr(327),
        'n': unichr(328),
        'R': unichr(344),
        'r': unichr(345),
        'S': unichr(352),
        's': unichr(353),
        'T': unichr(356),
        't': unichr(357),
        'Z': unichr(381),
        'z': unichr(382),
        'A': unichr(461),
        'a': unichr(462),
        'I': unichr(463),
        'i': unichr(464),
        'O': unichr(465),
        'o': unichr(466),
        'U': unichr(467),
        'u': unichr(468),
        'G': unichr(486),
        'g': unichr(487),
        'K': unichr(488),
        'k': unichr(489),
        'j': unichr(496),
        'H': unichr(542),
        'h': unichr(543),
    }

class H(Accent):
    chars = {
        'O': unichr(336),
        'o': unichr(337),
        'U': unichr(368),
        'u': unichr(369),
    }

class t(Accent):
    chars = {}

class c(Accent):
    chars = {
        'C': unichr(199),
        'c': unichr(231),
        'G': unichr(290),
        'g': unichr(123),
        'K': unichr(310),
        'k': unichr(311),
        'L': unichr(315),
        'l': unichr(316),
        'N': unichr(325),
        'n': unichr(326),
        'R': unichr(342),
        'r': unichr(343),
        'S': unichr(350),
        's': unichr(351),
        'T': unichr(354),
        't': unichr(355),
        'E': unichr(552),
        'e': unichr(553),
    }

class d(Accent):
    chars = {
        'B': unichr(7684),
        'b': unichr(7684),
        'D': unichr(7692),
        'd': unichr(7693),
        'H': unichr(7716),
        'h': unichr(7717),
        'K': unichr(7730),
        'k': unichr(7731),
        'L': unichr(7734),
        'l': unichr(7735),
        'M': unichr(7746),
        'm': unichr(7747),
        'N': unichr(7750),
        'n': unichr(7751),
        'R': unichr(7770),
        'r': unichr(7771),
        'S': unichr(7778),
        's': unichr(7779),
        'T': unichr(7788),
        't': unichr(7789),
        'V': unichr(7806),
        'v': unichr(7807),
        'W': unichr(7816),
        'w': unichr(7817),
        'Z': unichr(7826),
        'z': unichr(7827),
        'A': unichr(7840),
        'a': unichr(7841),
        'E': unichr(7864),
        'e': unichr(7865),
        'I': unichr(7882),
        'i': unichr(7883),
        'O': unichr(7884),
        'o': unichr(7885),
        'U': unichr(7908),
        'u': unichr(7909),
        'Y': unichr(7924),
        'y': unichr(7925),
    }

class b(Accent):
    chars = {
        'B': unichr(7686),
        'b': unichr(7687),
        'D': unichr(7694),
        'd': unichr(7695),
        'K': unichr(7732),
        'k': unichr(7733),
        'L': unichr(7738),
        'l': unichr(7739),
        'N': unichr(7752),
        'n': unichr(7753),
        'R': unichr(7774),
        'r': unichr(7775),
        'T': unichr(7790),
        't': unichr(7791),
        'Z': unichr(7828),
        'z': unichr(7829),
        'h': unichr(7830),
    }

class k(Accent):
    chars = {
        'A': unichr(260),
        'a': unichr(261),
        'E': unichr(280),
        'e': unichr(281),
        'I': unichr(302),
        'i': unichr(303),
        'U': unichr(370),
        'u': unichr(371),
        'O': unichr(490),
        'o': unichr(491),
    }

class r(Accent):
    chars = {}

#
# Table 3.2: Non-English Symbols (see Characters.py)
#

class Symbol(Command):
    pass

#class oe(Symbol): pass 
#class OE(Symbol): pass
#class ae(Symbol): pass
#class AE(Symbol): pass
#class aa(Symbol): pass
#class AA(Symbol): pass
#class o(Symbol): pass
#class O(Symbol): pass
#class l(Symbol): pass
#class L(Symbol): pass
#class ss(Symbol): pass
# ?`
# !`


#
# Special symbols
#

class dag(Symbol):
    unicode = unichr(8224)

class ddag(Symbol):
    unicode = unichr(8225)

class S(Symbol):
    unicode = unichr(167)

class P(Symbol):
    unicode = unichr(182)

class copyright(Symbol):
    unicode = unichr(169)

class pounds(Symbol):
    unicode = unichr(163)
