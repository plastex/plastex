#!/usr/bin/env python

from report import *

def ProcessOptions(options, document):
    import report
    report.ProcessOptions(options, document)
    document.context['thesection'].format = '${section}'
