#!/usr/bin/env python

import sys, re
from plasTeX import Base

try: import pygments
except: pygments = None

class listingsname(Base.Command):
    str = 'Listing'

PackageOptions = {}

def ProcessOptions(options, document):
    document.context.newcounter('listings',
                                resetby='chapter',
                                format='${thechapter}.${listings}')
    PackageOptions.update(options)

class lstset(Base.Command):
    args = 'arguments:dict'
    def invoke(self, tex):
        Base.Command.invoke(self, tex)
        if 'language' in list(self.attributes['arguments'].keys()):
            self.ownerDocument.context.current_language = \
                self.attributes['arguments']['language']

class lstlisting(Base.verbatim):
    args = '[ arguments:dict ]'
    counter = 'listings'

    def invoke(self, tex):
        if self.macroMode == Base.Environment.MODE_END:
            return
        s = ''.join(Base.verbatim.invoke(self, tex)[1:]).replace('\r','').split('\n')
        _format(self, s)

class lstinline(Base.verb):
    args = '[ arguments:dict ]'

    def invoke(self, tex):
        _format(self, ''.join(Base.verb.invoke(self, tex)[2:-1]))

class lstinputlisting(Base.Command):
    args = '[ arguments:dict ] file:str'
    counter = 'listings'

    def invoke(self, tex):
        Base.Command.invoke(self, tex)
        if 'file' not in list(self.attributes.keys()) or not self.attributes['file']:
            raise ValueError('Malformed \\lstinputlisting macro.')
        encoding = self.config['files']['input-encoding']
        _format(self, open(self.attributes['file'],  encoding=encoding))

def _format(self, file):
    if self.attributes['arguments'] is None:
        self.attributes['arguments'] = {}

    linenos = False
    if ('numbers' in list(self.attributes['arguments'].keys())
        or 'numbers' in list(PackageOptions.keys())):
        linenos = 'inline'

    # If this listing includes a label, inform plasTeX.
    if 'label' in list(self.attributes['arguments'].keys()):
        if hasattr(self.attributes['arguments']['label'], 'textContent'):
            self.ownerDocument.context.label(
                self.attributes['arguments']['label'].textContent)
        else:
            self.ownerDocument.context.label(
                self.attributes['arguments']['label'])

    # Check the textual LaTeX arguments and convert them to Python
    # attributes.
    if 'firstline' in list(self.attributes['arguments'].keys()):
        first_line_number = int(self.attributes['arguments']['firstline'])
    else:
        first_line_number = 0

    if 'lastline' in list(self.attributes['arguments'].keys()):
        last_line_number = int(self.attributes['arguments']['lastline'])
    else:
        last_line_number = sys.maxsize

    # Read the file, all the while respecting the "firstline" and
    # "lastline" arguments given in the document.
    self.plain_listing = ''
    for current_line_number, line in enumerate(file):
        current_line_number += 1
        if (current_line_number >= first_line_number) and \
           (current_line_number <= last_line_number):
            # Remove single-line "listings" comments. Only
            # comments started by "/*@" and ended by "@*/" are
            # supported.
            line = re.sub(r'/\*@[^@]*@\*/', '', line)

            # Add the just-read line to the listing.
            if hasattr(file, 'read'):
                self.plain_listing += line
            else:
                self.plain_listing += '\n' + line


    # Create a syntax highlighted XHTML version of the file using Pygments
    if pygments is not None:
        from pygments import lexers, formatters
        try:
            lexer = lexers.get_lexer_by_name(self.ownerDocument.context.current_language.lower())
        except Exception as msg:
            lexer = lexers.TextLexer()
        self.xhtml_listing = pygments.highlight(self.plain_listing, lexer, formatters.HtmlFormatter(linenos=linenos))
