#!/usr/bin/env python

import book
from book import *

def ProcessOptions(options, document):
    book.ProcessOptions(options, document)
    document.context['thesection'].format = '${section}'
