#!/usr/bin/env python

import codecs
from plasTeX.Config import config
from simpletal import simpleTAL, simpleTALES
from simpletal.simpleTALES import Context as TALContext
from simpletal.simpleTALUtils import FastStringOutput as StringIO

__all__ = ['htmltemplate', 'xmltemplate']

encoding = config['encoding']['output']

def _render(self, obj, outputFile=None, outputEncoding=encoding, interpreter=None):
    """ New rendering method for HTML templates """
    output = outputFile
    if obj.filename:
        output = codecs.open(obj.filename,'w',encoding)
    elif outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    self.expand(context, output, outputEncoding, interpreter)
    if obj.filename:
        output.close()
        return u''
    elif output is not None:
        return output.getvalue()
simpleTAL.HTMLTemplate.__call__ = _render
del _render

def _render(self, obj, outputFile=None, outputEncoding=encoding, docType=None, suppressXMLDeclaration=1, interpreter=None):
    """ New rendering method for XML templates """
    output = outputFile
    if obj.filename:
        output = codecs.open(obj.filename,'w',encoding)
    elif outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    self.expand(context, output, outputEncoding, docType, suppressXMLDeclaration, interpreter)
    if obj.filename:
        output.close()
        return u''
    elif output is not None:
        return output.getvalue()
simpleTAL.XMLTemplate.__call__ = _render
del _render

htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate
