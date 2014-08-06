#!/usr/bin/env python

import locale
import string

def stringletters():
    encoding = locale.getlocale()[1]
    if encoding:
        return unicode(string.letters, encoding)
    else:
        return unicode(string.letters)
