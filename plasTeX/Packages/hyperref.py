#!/usr/bin/env python

"""
Implementation of the hyperref package

TO DO:
- \autoref doesn't look for \*autorefname, it only looks for \*name
- Layouts
- Forms optional parameters

"""

from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Crossref import ref, pageref
from nameref import Nameref, nameref
import urlparse

def addBaseURL(self, urlarg):
    try:
        baseurl = self.ownerDocument.userdata['packages']['hyperref']['baseurl']
        return urlparse.urljoin(baseurl, self.attributes[urlarg])            
    except KeyError: pass
    return self.attributes[urlarg]

# Basic macros

ref.args = '* %s' % ref.args
pageref.args = '* %s' % pageref.args

class href(Command):
    args = 'url:url self'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.attributes['url'] = addBaseURL(self, 'url')
        return res

class url(Command):
    args = 'url:url'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.attributes['url'] = addBaseURL(self, 'url')
        return res

class nolinkurl(Command):
    args = 'url:url'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.attributes['url'] = addBaseURL(self, 'url')
        return res

class hyperbaseurl(Command):
    args = 'base:url'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        data = self.ownerDocument.userdata
        if 'packages' not in data:
            data['packages'] = {}
        if 'hyperref' not in data['packages']:
            data['packages']['hyperref'] = {}
        self.ownerDocument.userdata['packages']['hyperref']['baseurl'] = self.attributes['base']
        return res

class hyperimage(Command):
    args = 'url:url self'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.attributes['url'] = addBaseURL(self, 'url')
        return res

class hyperdef(Command):
    args = 'category name self'

class hyperref(Command):
    args = 'url:url category name self'
    def invoke(self, tex):
        res = Command.invoke(self, tex)
        self.attributes['url'] = addBaseURL(self, 'url')
        return res

class hyperlink(Command):
    args = 'label:idref self'

class hypertarget(Command):
    counter = 'hypertarget'  # so we can link to it
    args = 'label:id self'

class hypertargetname(Command):
    """ Dummy class for hypertarget macro """
    unicode = ''

class thehypertarget(Command):
    """ Dummy class for hypertarget macro """
    unicode = ''

class phantomsection(Command):
    pass

class autoref(Command):
    args = 'label:idref'

class pdfstringdef(Command):
    args = 'macroname:string tex:string'

class textorpdfstring(Command):
    args = 'tex:string pdf:string'

class pdfstringdefDisableCommands(Command):
    args = 'tex:string'

class hypercalcbp(Command):
    args = 'size:string'


# Forms

class Form(Environment):
    args = '[ parameters:dict ]'

class TextField(Command):
    args = '[ parameters:dict ] label'

class CheckBox(Command):
    args = '[ parameters:dict ] label'

class ChoiceMenu(Command):
    args = '[ parameters:dict ] label choices:list'

class PushButton(Command):
    args = '[ parameters:dict ] label'

class Submit(Command):
    args = '[ parameters:dict ] label'

class Reset(Command):
    args = '[ parameters:dict ] label'


class LayoutTextField(Command):
    args = 'label field'

class LayoutChoiceField(Command):
    args = 'label field'

class LayoutCheckField(Command):
    args = 'label field'


class MakeRadioField(Command):
    args = 'width height'

class MakeCheckField(Command):
    args = 'width height'

class MakeTextField(Command):
    args = 'width height'

class MakeChoiceField(Command):
    args = 'width height'

class MakeButtonField(Command):
    args = 'self'


class DefaultHeightofSubmit(Command):
    args = 'size:dimen'

class DefaultWidthofSubmit(Command):
    args = 'size:dimen'

class DefaultHeightofReset(Command):
    args = 'size:dimen'

class DefaultWidthofReset(Command):
    args = 'size:dimen'

class DefaultHeightofCheckBox(Command):
    args = 'size:dimen'

class DefaultWidthofCheckBox(Command):
    args = 'size:dimen'

class DefaultHeightofChoiceMenu(Command):
    args = 'size:dimen'

class DefaultWidthofChoiceMenu(Command):
    args = 'size:dimen'

class DefaultHeightofText(Command):
    args = 'size:dimen'

class DefaultWidthofText(Command):
    args = 'size:dimen'    
    
class pdfbookmark(Command):
    args = '[level:number] text name'

class currentpdfbookmark(Command):
    args = 'text name'

class subpdfbookmark(Command):
    args = 'text name'

class belowpdfbookmark(Command):
    args = 'text name'