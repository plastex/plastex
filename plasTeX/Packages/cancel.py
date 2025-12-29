"""
Implement the commands from the LaTeX ``cancel`` package: https://ctan.org/pkg/cancel

In math mode, MathJax implements these commands so they're passed through unmodified.

In text mode, the HTML5 renderer renders these as ``<del>`` elements.
"""

from plasTeX import Command


class cancel(Command):
    args = 'self'

class bcancel(Command):
    args = 'self'

class xcancel(Command):
    args = 'self'

class cancelto(Command):
    args = 'to content'
