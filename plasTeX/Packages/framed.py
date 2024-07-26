"""
The framed package (https://ctan.org/pkg/framed) provides environments which
put their contents in a frame.

This adds a plasTeX implementation of the framed environments, and some
basic styling in the HTML5 renderer.

Only the standard environments ``framed``, ``oframed``, ``shaded``,
``shaded*``, ``snugshade``, ``snugshade*`` and ``leftbar`` are implemented.

None of the commands listed under "Expert commands" in the framed documentation
are implemented, and the framed environments don't use the lengths
``\FrameRule`` or ``\FrameSep``.
"""


from plasTeX import Environment


class framed(Environment):
    pass


class oframed(framed):
    pass


class shaded(framed):
    shaded = True
    pass


class shadedStar(shaded):
    macroName = 'shaded*'


class snugshade(shaded):
    pass


class snugshadeStar(snugshade):
    macroName = 'snugshade*'


class leftbar(framed):
    pass
