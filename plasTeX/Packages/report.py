#!/usr/bin/env python

from plasTeX.Packages.book import *
from plasTeX.Packages import book

def ProcessOptions(options, document):
    book.ProcessOptions(options, document)
    document.context['theequation'].format = '${equation}'
