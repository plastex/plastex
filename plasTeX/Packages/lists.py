#!/usr/bin/env python

from plasTeX.Utils import *
from plasTeX import Environment, Command

class List(Environment):
    """ Base class for all list-based environments """

    block = True

    class item(Command):
        args = '[ term ]'
        def digest(self, tokens):
            attrs = self.attributes
            Command.digest(self, tokens)
            if attrs['term']:
                attrs['term'][:] = paragraphs(attrs['term'],
                                          type(type(self).context['par']))
            return self

    def digest(self, tokens):
        Environment.digest(self, tokens)
        listitem = type(self).item
        items = []
        while self and not isinstance(self[0], listitem):
            self.pop(0)
        if self:
            items.append(self.pop(0))
        while self:
            while self and not isinstance(self[0], listitem):
                items[-1].append(self.pop(0))
            if self:
                items.append(self.pop(0))
        for item in items:
            item[:] = paragraphs(item, type(type(self).context['par']))
        self[:] = items
        return self

class description(List): pass
class _list(List): texname = 'list'
class itemize(List): pass
class enumerate(List): pass
