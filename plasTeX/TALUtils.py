#!/usr/bin/env python

import codecs
from plasTeX.Config import config
from plasTeX.Logging import getLogger, ERROR
from simpletal import simpleTAL, simpleTALES
from simpletal.simpleTALES import Context as TALContext
from simpletal.simpleTALUtils import FastStringOutput as StringIO
from StringIO import StringIO

stlog = getLogger('simpleTAL')
stelog = getLogger('simpleTALES')

stlog.setLevel(ERROR)
stelog.setLevel(ERROR)

__all__ = ['htmltemplate', 'xmltemplate']

encoding = config['encoding']['output']

def applyTemplates(obj):
    if not self.hasChildNodes():
        return u''
    if self.filename:
        status.info(' [ %s ', self.filename)
    s = []
    for child in self.childNodes:
        val = Node.renderer.get(child.nodeName, unicode)(child)
        if type(val) is unicode:
            s.append(val)
        else:
            s.append(unicode(val,encoding))
    if self.filename:
        status.info(' ] ')
    return u''.join(s)

def _render(self, obj, outputFile=None, outputEncoding=encoding, interpreter=None):
    """ New rendering method for HTML templates """
    output = outputFile
    if obj.filename or outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    self.expand(context, output, outputEncoding, interpreter)
    if obj.filename:
        obj.renderer.write(obj.filename, output.getvalue())
        return u''
    else:
        return output.getvalue()
simpleTAL.HTMLTemplate.__call__ = _render
del _render

def _render(self, obj, outputFile=None, outputEncoding=encoding, docType=None, suppressXMLDeclaration=1, interpreter=None):
    """ New rendering method for XML templates """
    output = outputFile
    if obj.filename or outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    self.expand(context, output, outputEncoding, docType, suppressXMLDeclaration, interpreter)
    if obj.filename:
        obj.renderer.write(obj.filename, output.getvalue())
        return u''
    else:
        return output.getvalue()
simpleTAL.XMLTemplate.__call__ = _render
del _render

htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate
