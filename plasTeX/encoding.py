#!/usr/bin/env python

import locale
import string

def stringletters():
    encoding = locale.getlocale()[1]
    if encoding:
        return str(string.ascii_letters)
    else:
        return str(string.ascii_letters)
