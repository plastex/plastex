#!/usr/bin/env python

import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class XHTML(_Renderer):
    """ Renderer for XHTML documents """

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def cleanup(self, document, files, postProcess=None):
        res = _Renderer.cleanup(self, document, files, postProcess=postProcess)
        self.doJavaHelpFiles(document, version='1')
        self.doJavaHelpFiles(document, version='2')
        self.doEclipseHelpFiles(document)
        self.doCHMFiles(document)
        return res

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Force XHTML syntax on empty tags
        s = re.compile(r'(<(?:hr|br|img|link|meta|col)\b.*?)\s*/?\s*(>)', 
                       re.I|re.S).sub(r'\1 /\2', s)

        # Remove empty paragraphs
        s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Add a non-breaking space to empty table cells
        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)
        
        return s
    
    def doCHMFiles(self, document, encoding='ISO-8859-1'):
        """ Generate files needed to for CHM help files """
        latexdoc = document.getElementsByTagName('document')[0]
        
        # Create table of contents
        if 'chm-toc' in self:
            toc = self['chm-toc'](latexdoc)
            #toc = re.sub(r'\s*</li>', r'', toc)
            toc = re.sub(r'\s*/\s*>', r'>', toc)
            toc = re.sub(r'(<param)(\s+[^>]*)(\s+name="[^"]*")(\s*>)', r'\1\3\2\4', toc)
            f = codecs.open('chm.hhc', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">\n')
            f.write(toc)
            f.close()

        # Create index file
        if 'chm-index' in self:
            idx = self['chm-index'](latexdoc)
            #idx = re.sub(r'\s*</li>', r'', toc)
            idx = re.sub(r'\s*/\s*>', r'>', idx)
            idx = re.sub(r'(<param)(\s+[^>]*)(\s+name="[^"]*")(\s*>)', r'\1\3\2\4', idx)
            f = codecs.open('chm.hhk', 'w', encoding, errors='xmlcharrefreplace')
            f.write('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">\n')
            f.write(idx)
            f.close()

        # Create help file
        if 'chm-help' in self:
            help = self['chm-help'](latexdoc)
            f = codecs.open('chm.hhp', 'w', encoding, errors='xmlcharrefreplace')
            f.write(help)
            f.close()

    def doEclipseHelpFiles(self, document, encoding='ISO-8859-1'):
        """ Generate files needed to use HTML as Eclipse Help """
        latexdoc = document.getElementsByTagName('document')[0]
        
        # Create table of contents
        if 'eclipse-toc' in self:
            toc = self['eclipse-toc'](latexdoc)
            f = codecs.open('eclipse-toc.xml', 'w', encoding, errors='xmlcharrefreplace')
            toc = re.sub(r'(<topic\b[^>]*[^/])\s*>\s*</topic>', r'\1 />', toc)
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(toc)
            f.close()

        # Create plugin file
        if 'eclipse-plugin' in self:
            toc = self['eclipse-plugin'](latexdoc)
            f = codecs.open('eclipse-plugin.xml', 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(toc)
            f.close()

        # Create index file
        if 'eclipse-index' in self:
            toc = self['eclipse-index'](latexdoc)
            f = codecs.open('eclipse-index.xml', 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(toc)
            f.close()

    def doJavaHelpFiles(self, document, encoding='ISO-8859-1', version='2'):
        """ Generate files needed to use HTML as Java Help """
        latexdoc = document.getElementsByTagName('document')[0]
        version = str(version)
        
        # Create table of contents
        if ('javahelp-toc-'+version) in self:
            toc = self['javahelp-toc-'+version](latexdoc)
            toc = re.sub(r'(<tocitem\b[^>]*[^/])\s*>\s*</tocitem>', r'\1 />', toc)
            f = codecs.open('javahelp%s-toc.xml' % version, 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(toc)
            f.close()

        # Create index
        if ('javahelp-index-'+version) in self and latexdoc.index:
            idx = self['javahelp-index-'+version](latexdoc)
            idx = re.sub(r'(\n\s*)+', r'\n', idx)
            f = codecs.open('javahelp%s-index.xml' % version, 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(idx)
            f.close()

        # Create map file
        if ('javahelp-map-'+version) in self:
            idx = self['javahelp-map-'+version](latexdoc)
            idx = re.sub(r'(\n\s*)+', r'\n', idx)
            f = codecs.open('javahelp%s.jhm' % version, 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(idx)
            f.close()

        # Create helpset file
        if ('javahelp-helpset-'+version) in self:
            idx = self['javahelp-helpset-'+version](latexdoc)
            idx = re.sub(r'(\n\s*)+', r'\n', idx)
            f = codecs.open('javahelp%s.hs' % version, 'w', encoding, errors='xmlcharrefreplace')
            f.write("<?xml version='1.0' encoding='%s' ?>\n" % encoding)
            f.write(idx)
            f.close()

Renderer = XHTML 
