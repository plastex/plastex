#!/usr/bin/env python

"""
C.11.3 Bibliography and Citation (p208)

"""

import string, plasTeX
from plasTeX.Base.LaTeX.Sectioning import section, chapter
from plasTeX import Command, Environment, TeXFragment
from plasTeX.Tokenizer import Token
from Lists import List

log = plasTeX.Logging.getLogger()

class bibliography(chapter):
    args = 'files:str'

    bibitems = {}
    title = 'References'

    def invoke(self, tex):
        res = super(bibliography, self).invoke(tex)
        self.attributes['title'] = bibliography.title

        tex.loadAuxiliaryFile()

        # Load bibtex file
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
        numitems = 0

        def invoke(self, tex):
            res = List.item.invoke(self, tex)
            # Put the entry into the global bibliography
            bibliography.bibitems[self.attributes['key']] = self
            thebibliography.bibitem.numitems += 1
            self.ref = str(thebibliography.bibitem.numitems)
            return res

        def id(self):
            return self.attributes['key']
        id = property(id)

        def cite(self):
            res = TeXFragment()
            res.extend(bibcite.citations.get(self.attributes['key']))
            res.idref = self
            return res

        def citation(self):
            return self.cite()

    def digest(self, tokens):
        for tok in tokens:
            if not isinstance(tok, thebibliography.bibitem):
                continue
            tokens.push(tok)
            break
        return List.digest(self, tokens)

class cite(Command):
    args = '[ text ] keys:list:str'

    def bibitems(self):
        # Get all referenced items
        return [bibliography.bibitems.get(x) for x in self.attributes['keys']]
    bibitems = property(bibitems)

    def postnote(self):
        a = self.attributes
        if a['text'] is not None:
            return a['text']
        return ''
    postnote = property(postnote)

    def citation(self):
        res = []
        res.append('[')
        for item in self.bibitems:
            res.append(item)
            res.append(', ')
        res.pop()
        res.append(self.postnote + ']')
        return res
            
class nocite(Command):
    args = 'keys:str'

class bibcite(Command):
    citations = {}
    args = 'key:str info'

    def invoke(self, tex):
        Command.invoke(self, tex)
        value = self.attributes['info'].firstChild
        self.citations[self.attributes['key']] = value

class citation(Command):
    pass

class bibstyle(Command):
    pass

class bibdata(Command):
    pass
