#!/usr/bin/env python

from types import SliceType as _SliceType

class ordereddict(dict):
    """ 
    Dictionary where key/value pairs are kept in the original order

    Every method in this dictionary-based class returns its results
    in the same order in which they were inserted into the dictionary.
    If the same key is inserted twice, it is inserted into the location
    of the original insertion.

    """

    def __iter__(self):
        return iter(self.keys())

    iterkeys = __iter__

    def iteritems(self):
        return iter(self.items())

    def itervalues(self):
        return iter(self.values())

    def popitem(self):
        if not hasattr(self, '_keys'): self._keys = []
        key = self._keys.pop(0)
        value = self[key]
        del self[key]
        return (key, value)

    def items(self):
        if not hasattr(self, '_keys'): self._keys = []
        return [(x,self[x]) for x in self._keys] 

    def keys(self):
        if not hasattr(self, '_keys'): self._keys = []
        return self._keys

    def values(self):
        if not hasattr(self, '_keys'): self._keys = []
        return [self[x] for x in self._keys] 

    def __setitem__(self, key, value):
        if not hasattr(self, '_keys'): self._keys = []
        if key not in self._keys:
            self._keys.append(key)
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        if not hasattr(self, '_keys'): self._keys = []
        self._keys = [x for x in self._keys if x != key]
        dict.__delitem__(self, key)

    def __getitem__(self, key):
        if type(key) == _SliceType:
            return self.__getslice__(key.start, key.stop)
        return dict.__getitem__(self, key)

    def update(self, other):
        for key, value in other.items():
            self[key] = value

    def __getslice__(self, start, stop):
        keys = self.keys()
        if start is None:
           start = 0
        else:
           start = max(0,keys.index(start)-1)
        if stop is None:
           stop = len(keys)
        else:
           stop = keys.index(stop)
        return [self[x] for x in keys[start:stop]]

    def __delslice__(self, start, stop):
        keys = self.keys()
        if start is None:
           start = 0
        else:
           start = keys.index(start)
        if stop is None:
           stop = len(keys)
        else:
           stop = keys.index(stop)
        for x in keys[start:stop]:
            dict.__delitem__(self, x)


class sorteddict(ordereddict):
    """ 
    Dictionary where key/value pairs are sorted by their key

    Every method in this dictionary-based class returns its results
    in the same ordered as if its keys were sorted.

    """

    def __setitem__(self, key, value):
        if not hasattr(self, '_keys'): self._keys = []
        if key not in self._keys:
            self._keys.append(key)
        self._keys.sort()
        dict.__setitem__(self, key, value)
