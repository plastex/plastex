#!/usr/bin/env python

"""
C.11.3 Bibliography and Citation (p208)

"""

from plasTeX.Base.LaTeX.Sectioning import section
from plasTeX import Command, Environment
from Lists import List
from plasTeX.Logging import getLogger

log = getLogger()

class bibliography(section):
    args = 'files:str'

    bibitems = {}

    def invoke(self, tex):
        a = self.parse(tex)
        a['title'] = 'References'
        try:
            file = tex.kpsewhich(self.ownerDocument.userdata['jobname'], ['.bbl'])
            tex.input(open(file))
        except OSError, msg:
            log.warning(msg)

class bibliographystyle(Command):
    args = 'style'
    
class thebibliography(List):
    args = 'widelabel'
  
    class bibitem(List.item):
        args = '[ label ] key:str'
        def invoke(self, tex):
            res = List.item.invoke(self, tex)
            bibliography.bibitems[self.attributes['key']] = self
            return res
        def ref(self):
            return self.attributes['label']
        ref = property(ref)
        def id(self):
            return self.attributes['key']
        id = property(id)
        
    def digest(self, tokens):
        for tok in tokens:
            if not isinstance(tok, thebibliography.bibitem):
                continue
            tokens.push(tok)
            break
        return List.digest(self, tokens)

class cite(Command):
    args = '[ text ] key:str'
    def idref(self):
        return bibliography.bibitems.get(self.attributes['key'])
    idref = property(idref)

class nocite(Command):
    args = 'keys:str'
