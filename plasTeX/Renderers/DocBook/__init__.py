#!/usr/bin/env python
import re
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class DocBook(_Renderer):
    """ Renderer for DocBook documents """
    fileExtension = '.xml'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']
    
    def preclean(self, document):
        self.document = document
        # fix paras and do mathml if needed
        super(DocBook, self).preclean(document)
        # fix quotes and figures
        self.walk(document, self.fix_quote)
        self.walk(document, self.fix_figure)
 
    
    def fix_figure(self, node):
        """Checks for bad paragraphs inside figures"""
        child = node.firstChild
        if node.nodeName != 'figure' or child.nodeName != 'par':
            return

        self.unpack(child)

    def fix_quote(self, node):
        """Checks for quote text not wrapped in a paragraph."""
        children = node.childNodes
        if (node.nodeName not in ['quote', 'quotation'] 
            or len(children) == 0 
            or children[0].nodeName == 'par'):
            return

        # if the quote contains bare text, wrap it in a par
        par = self.document.createElement('par')
        par.extend(children)
        while node.childNodes:
            node.pop(-1)
        node.insert(0, par)

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        return res

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)
        s = re.compile(r'</partintro>\s*<partintro>',re.I).sub(r'',s)
        #
        s = re.compile(r'<para>\s*(<articleinfo>)',re.I).sub(r'\1',s)
        s = re.compile(r'(</articleinfo>)\s*</para>',re.I).sub(r'\1',s)
        #
        s = re.compile(r'(<informalfigure>)\s*<para>',re.I).sub(r'\1',s)
        s = re.compile(r'</para>\s*(</informalfigure>)',re.I).sub(r'\1',s)
        #
        s = re.compile(r'(<para>)(\s*<para>)+',re.I).sub(r'\1',s)
        s = re.compile(r'(</para>\s*)+(</para>)',re.I).sub(r'\2',s)
        #
#        s = s.replace('&','&amp;')
        #
        s = re.compile(r'<para>\s*</para>', re.I).sub(r'', s)
        return s
    
Renderer = DocBook
