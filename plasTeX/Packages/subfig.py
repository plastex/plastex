#!/usr/bin/env python

"""
subfig package

TO-DO
- Options handling
- Only works with figure environment
- Lists of floats

"""

import new
from plasTeX import Command, Environment
from plasTeX.Base.LaTeX.Floats import Float

def ProcessOptions(options, document):
    context = document.context
    context.newcounter('subfloat', resetby='figure', format='${subfloat.alph}')

class newsubfloat(Command):
    args = '[ options:dict ] name:str'
    def invoke(self, tex):
        Command.invoke(self, tex)
        c = self.ownerDocument.context
        name = str(self.attributes['name'])
        options = self.attributes['options'] or {}

        # Create new subfloat class
        newclass = new.classobj(name, (subfloat,), 
                                {'options':options,'counter':name})
        c.addGlobal(name, newclass)

        # Create new counter
        c.newcounter(name, resetby='figure', format='${%s.alph}' % name)

        # Create the float name macro
        c.newcommand(name+'name', 0, name)

class DeclareCaptionListOfFormat(Command):
    args = 'keyword code'

class subfloatname(Command):
    unicode = ''

class subfloat(Command):
    args = '[ toc ] [ caption ] self'
    counter = 'subfloat'
    options = {}

    def preParse(self, tex):
        """
        This is getting tricky.  The ContinuedFloat tells whether or not 
        the counter should be incremented.  We save the lastvalue of the
        counter in the userdata so we can get it back here.

        """
        doc = self.ownerDocument
        c = doc.context

        if doc.userdata.getPath('packages/subfig/continued'):
            v = doc.userdata.getPath('packages/subfig/subfloats/%s/lastvalue' % 
                                     self.tagName, 1)
            c.counters[self.counter].setcounter(v+1)
            doc.userdata.setPath('packages/subfig/continued', False)
        else:
            doc.userdata.setPath('packages/subfig/subfloats/%s/lastvalue' % 
                                 self.tagName, c.counters[self.counter].value)

        return Command.preParse(self, tex)

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.title = self.attributes['caption'] or self.attributes['toc']

    def ref():
        """
        This is a bit crazy.  We have to override ref so that we can
        add some new functionality.  The value normally gotten by ref
        is now held in subref.  The ref value also contains the ref value
        of the parent float node.

        """
        def fset(self, value):
            self.subref = value
        def fget(self):
            # Find the parent float of this subfloat
            node = self.parentNode
            while node is not None and not(isinstance(node, Float)):
                node = node.parentNode
            parentFloat = node
    
            # Add the float number to the ref value
            doc = self.ownerDocument
            frag = doc.createDocumentFragment()
            frag.append(parentFloat.caption.ref)
            frag.append(self.subref)
            return frag
        return locals()
    ref = property(**ref())
        
class subref(Command):
    args = '* label:idref'
        
class ContinuedFloat(Command):
    def invoke(self, tex):
        Command.invoke(self, tex)
        doc = self.ownerDocument
        c = doc.context
        c.counters['figure'].value -= 1
        doc.userdata.setPath('packages/subfig/continued', True)

class listsubcaptions(Command):
    pass

class captionsetup(Command):
    args = '[ type:str ] options:dict'
