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
