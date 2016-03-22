#!/usr/bin/env python

from plasTeX.Packages.book import *

def ProcessOptions(options, document):
    from plasTeX.Packages import book
    book.ProcessOptions(options, document)
    document.context['theequation'].format = '${equation}'
