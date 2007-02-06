#!/usr/bin/env python

from report import *

def ProcessOptions(options, document):
    import report
    report.ProcessOptions(options, document)
    document.context['thesection'].format = '${section}'
    theindex.counter = 'section'
    theindex.level = Environment.SECTION_LEVEL
    printindex.counter = 'section'
    printindex.level = Command.SECTION_LEVEL
    bibliography.counter = 'section'
    bibliography.level = Command.SECTION_LEVEL
