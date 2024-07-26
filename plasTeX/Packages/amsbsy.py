"""
A dummy implementation of the amsbsy package (https://ctan.org/pkg/amsbsy).

The ``\pmb`` and ``\boldsymbol`` commands are handled by the maths renderer.
"""

from plasTeX import Command

class pmb(Command):
    pass

class boldsymbol(Command):
    pass
