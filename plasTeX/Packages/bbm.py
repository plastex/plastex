"""
The bbm package (https://ctan.org/pkg/bbm) provides a "blackboard bold" font, and a ``\mathbbm`` command to use that font.

In this implementation, ``\mathbbm`` is rewritten to ``\mathbb``.
"""

from plasTeX import Command, sourceArguments

class mathbbm(Command):
    args = 'self'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
