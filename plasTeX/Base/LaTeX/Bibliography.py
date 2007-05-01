#!/usr/bin/env python

"""
C.11.3 Bibliography and Citation (p208)

"""

import plasTeX, codecs
from plasTeX.Base.LaTeX.Sectioning import chapter
from plasTeX import Command, Environment
from Lists import List

log = plasTeX.Logging.getLogger()

class bibliography(chapter):
    args = 'files:str'

    bibitems = {}
    title = 'References'
    linkType = 'bibliography'

    def invoke(self, tex):
        res = chapter.invoke(self, tex)
        self.attributes['title'] = bibliography.title
        # Load bibtex file
        try:
            file = tex.kpsewhich(tex.jobname+'.bbl')
            tex.input(codecs.open(file, 'r', self.ownerDocument.config['files']['input-encoding']))
        except OSError, msg:
            log.warning(msg)

class bibliographystyle(Command):
    args = 'style'
    
class thebibliography(List):
    args = 'widelabel'
    linkType = 'bibliography'
  
    class bibitem(List.item):
        args = '[ label ] key:str'
        numitems = 0

        def invoke(self, tex):
            res = List.item.invoke(self, tex)
            a = self.attributes
            # Put the entry into the global bibliography
            bibliography.bibitems[a['key']] = self
            thebibliography.bibitem.numitems += 1
            self.ref = str(thebibliography.bibitem.numitems)
            key = a['key']
            label = a.get('label')
            if not bibcite.citations.has_key(key):
                if label is None:
                    label = self.ownerDocument.createDocumentFragment()
                    label.extend(self.ref)
                bibcite.citations[key] = label
            return res

        @property
        def id(self):
            return self.attributes['key']

        def cite(self):
            res = self.ownerDocument.createDocumentFragment()
            res.extend(bibcite.citations.get(self.attributes['key']))
            res.idref = self
            return res

        def citation(self):
            return self.cite()

    def digest(self, tokens):
        if self.macroMode == Command.MODE_END:
            return
        for tok in tokens:
            if not isinstance(tok, thebibliography.bibitem):
                continue
            tokens.push(tok)
            break
        return List.digest(self, tokens)

class cite(Command):
    args = '[ text ] keys:list:str'

    @property
    def bibitems(self):
        # Get all referenced items
        output = []
        for x in self.attributes['keys']:
            item = bibliography.bibitems.get(x)
            if item is None:
                log.warning('Bibliography item "%s" has no entry', x)
            else:
                output.append(item)
        return output

    @property
    def postnote(self):
        a = self.attributes
        if a['text'] is not None:
            return a['text']
        return ''

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
