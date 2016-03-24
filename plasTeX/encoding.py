#!/usr/bin/env python

import locale
import string

def stringletters():
    encoding = locale.getlocale()[1]
    if encoding:
        return string.letters.decode(encoding)
    else:
        return string.ascii_letters
