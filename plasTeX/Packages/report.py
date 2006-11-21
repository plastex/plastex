#!/usr/bin/env python

from book import *

def ProcessOptions(options, document):
    import book
    book.ProcessOptions(options, document)
    document.context['theequation'].format = '${equation}'
