#!/usr/bin/env python

from simpletal import simpleTAL, simpleTALES
from simpletal.simpleTALES import Context as TALContext
try: from cStringIO import StringIO
except: from StringIO import StringIO

__all__ = ['htmltemplate', 'xmltemplate']

encoding='utf-8'

def _render(self, obj, outputFile=None, outputEncoding=encoding, interpreter=None):
    """ New rendering method for HTML templates """
    output = outputFile
    if outputFile is None:
        output = StringIO()
    context = TALContext()
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
#   context.addGlobal('context', type(obj).context)
#   context.addGlobal('renderer', type(obj).context.renderer)
    self.expand(context, output, outputEncoding, interpreter)
    if output is not None:
        output.seek(0)
        return output.read()
simpleTAL.HTMLTemplate.__call__ = _render
del _render

def _render(self, obj, outputFile=None, outputEncoding=encoding, docType=None, suppressXMLDeclaration=1, interpreter=None):
    """ New rendering method for XML templates """
    output = outputFile
    if outputFile is None:
        output = StringIO()
    context = TALContext()
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
#   context.addGlobal('context', type(obj).context)
#   context.addGlobal('renderer', type(obj).context.renderer)
    self.expand(context, output, outputEncoding, docType, suppressXMLDeclaration, interpreter)
    if output is not None:
        output.seek(0)
        return output.read()
simpleTAL.XMLTemplate.__call__ = _render
del _render

htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate
