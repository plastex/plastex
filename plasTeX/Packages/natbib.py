#!/usr/bin/env python

"""
natbib

TODO: 
    - sort&compress (sort works, compress doesn't)

"""

import plasTeX
from plasTeX import Base, Node
from plasTeX.Base.LaTeX.Sectioning import chapter, section

log = plasTeX.Logging.getLogger()

PackageOptions = {}

def ProcessOptions(options, document):
    """ Process package options """
    context = document.context
    if options is None:
        return
    PackageOptions.update(options)
    for key, value in options.items():
        if key == 'numbers':
            bibpunct.punctuation['style'] = 'n'
            ProcessOptions({'square':True, 'comma':True}, document)
        elif key == 'super':
            bibpunct.punctuation['style'] = 's'
            bibpunct.punctuation['open'] = ''
            bibpunct.punctuation['close'] = ''
        elif key == 'authoryear':
            ProcessOptions({'round':True, 'colon':True}, document)
        elif key == 'round':
            bibpunct.punctuation['open'] = '('
            bibpunct.punctuation['close'] = ')'
        elif key == 'square':
            bibpunct.punctuation['open'] = '['
            bibpunct.punctuation['close'] = ']'
        elif key == 'angle':
            bibpunct.punctuation['open'] = '<'
            bibpunct.punctuation['close'] = '>'
        elif key == 'curly':
            bibpunct.punctuation['open'] = '{'
            bibpunct.punctuation['close'] = '}'
        elif key == 'comma':
            bibpunct.punctuation['sep'] = ','
        elif key == 'colon':
            bibpunct.punctuation['sep'] = ';'
        elif key == 'sectionbib':
            Base.bibliography.level = Base.section.level
        elif key == 'sort':
            pass
        elif key in ['sort&compress','sortandcompress']:
            pass
        elif key == 'longnamesfirst':
            pass
        elif key == 'nonamebreak':
            pass

class bibliography(Base.bibliography):

    class setcounter(Base.Command):
        # Added so that setcounters in the aux file don't mess counters up
        args = 'name:nox num:nox'

    def loadBibliographyFile(self, tex):
        doc = self.ownerDocument
        # Clear out any bib info from the standard package.  
        # We have to get our info from the aux file.
        doc.userdata.setPath('bibliography/bibcites', {})
        self.ownerDocument.context.push(self)
        self.ownerDocument.context['setcounter'] = self.setcounter
        tex.loadAuxiliaryFile()
        self.ownerDocument.context.pop(self)
        Base.bibliography.loadBibliographyFile(self, tex)

class bibstyle(Base.Command):
    args = 'style:str'

class bibliographystyle(Base.Command):
    args = 'style:str'

    styles = {
        'plain'  : ['[',']',',','n','',','],
        'plainnat':['[',']',',','a',',',','],
        'chicago': '();a,,',
        'chicago': '();a,,',
        'named'  : '[];a,,',
        'agu'    : ['[',']',';','a',',',', '],
        'egs'    : '();a,,',
        'agsm'   : ['(',')',';','a','',','],
        'kluwer' : ['(',')',';','a','',','],
        'dcu'    : '();a;,',
        'aa'     : ['(',')',';','a','',','],
        'pass'   : '();a,,',
        'anngeo' : '();a,,',
        'nlinproc':'();a,,',
        'cospar' : ['/','/',',','n','',''],
        'esa'    : ['(Ref. ',')',',','n','',''],
        'nature' : ['','',',','s','',','],
    }

    def invoke(self, tex):
        res = Base.Command.invoke(self, tex)
        try: 
            s = self.styles[self.attributes['style']]
        except KeyError:
        #    log.warning('Could not find bibstyle: "%s"',
        #                 self.attributes['style'])
            return res
        p = bibpunct.punctuation
        p['open']  = s[0]
        p['close'] = s[1]
        p['sep']   = s[2]
        p['style'] = s[3]
        p['dates'] = s[4]
        p['years'] = s[5]
        return res    
        
class bibpunct(Base.Command):
    """ Set up punctuation of citations """
    args = '[ post:str ] open:str close:str sep:str ' + \
           'style:str dates:str years:str'
    punctuation = {'post':', ', 'open':'(', 'close':')', 'sep':';', 
                   'style':'a', 'dates':',', 'years':','}

    def invoke(self, tex):
        res = Base.Command.invoke(self, tex)
        for key, value in self.attributes.items():
            if value is None:
                continue
            elif type(value) == str or type(value) == unicode:
                bibpunct.punctuation[key] = value
            else:
                bibpunct.punctuation[key] = value.textContent            
        return res

class bibcite(Base.Command):
    """ Auxiliary file information """
    args = 'key:str info'

    def invoke(self, tex):
        Base.Command.invoke(self, tex)
        value, year, author, fullauthor = list(self.attributes['info'])
        value.attributes['year'] = year
        value.attributes['author'] = author
        if not fullauthor.textContent.strip():
            value.attributes['fullauthor'] = author
        else:
            value.attributes['fullauthor'] = fullauthor
        doc = self.ownerDocument
        bibcites = doc.userdata.getPath('bibliography/bibcites', {})
        bibcites[self.attributes['key']] = value
        doc.userdata.setPath('bibliography/bibcites', bibcites)

class thebibliography(Base.thebibliography):

    class bibitem(Base.thebibliography.bibitem):

        @property
        def bibcite(self):
            try: 
                doc = self.ownerDocument
                return doc.userdata.getPath('bibliography/bibcites', {})[self.attributes['key']]
            except KeyError, msg:
                pass
            # We don't have a citation that matches, fill the fields
            # with dummy data
            value = self.ownerDocument.createElement('citation')
            value.parentNode = self
            value.append('??')
            for item in ['year','author','fullauthor']:
                obj = self.ownerDocument.createDocumentFragment()
                obj.parentNode = value
                obj.append('??')
                value.attributes[item] = obj
            return value

    
class harvarditem(thebibliography.bibitem):
    args = '[ abbrlabel ] label year key:str'

class NatBibCite(Base.cite):
    """ Base class for all natbib-style cite commands """
    args = '* [ text ] [ text2 ] keys:list:str'

    @property
    def bibitems(self):
        items = []
        doc = self.ownerDocument
        b = doc.userdata.getPath('bibliography/bibitems', {})
        for key in self.attributes['keys']:
            if key in b:
                items.append(b[key])
        if PackageOptions.has_key('sort') or \
           PackageOptions.has_key('sort&compress') or \
           PackageOptions.has_key('sortandcompress'):
            items.sort(lambda x, y: int(x.ref) - int(y.ref))
        return items

    @property
    def prenote(self):
        """ Text that comes before the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            out = self.ownerDocument.createDocumentFragment()
            out.extend(a['text'])
            out.append(' ')
            return out
        return ''

    @property
    def postnote(self):
        """ Text that comes after the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            out = self.ownerDocument.createDocumentFragment()
            out.append(bibpunct.punctuation['post'])
            out.extend(a['text2'])
            return out
        elif a.get('text') is not None:
            out = self.ownerDocument.createDocumentFragment()
            out.append(bibpunct.punctuation['post'])
            out.extend(a['text'])
            return out
        return ''
        
    @property
    def separator(self):
        """ Separator for multiple items """
        return bibpunct.punctuation['sep']

    def selectAuthorField(self, full=False):
        """ Determine if author should be a full name or shortened """
        if full:
            return 'fullauthor'
        doc = self.ownerDocument        
        # longnamesfirst means that only the first reference
        # gets the full length name, the rest use short names.
        cited = doc.userdata.getPath('bibliography/cited', [])
        if 'longnamesfirst' in PackageOptions and \
           self.attributes['key'] not in cited:
            full = True
            cited.append(self.attributes['key'])
        doc.userdata.setPath('bibliography/cited', cited)
        if full:
            return 'fullauthor'
        return 'author'
        
    def isNumeric(self):
        return bibpunct.punctuation['style'] in ['n','s']
        
    def isSuperScript(self):
        return bibpunct.punctuation['style'] == 's'

    def citeValue(self, item):
        """ Return cite value based on current style """
        if bibpunct.punctuation['style'] in ['n','s']:
            b = self.ownerDocument.createElement('bibliographyref')
            b.idref['bibitem'] = item
            b.append(item.bibcite)
            return b
        return item.bibcite.attributes['year']

    def capitalize(self, item):
        """ Capitalize the first text node """
        item = item.cloneNode(True)
        textnodes = [x for x in item.allChildNodes
                       if x.nodeType == self.TEXT_NODE]
        if not textnodes:
            return item
        node = textnodes.pop(0)
        node.parentNode.replaceChild(node.cloneNode(True).capitalize() ,node)
        return item        
            
# class citep(NatBibCite):

#     def numcitation(self):
#         """ Numeric style citations """
#         res = []
#         res.append(bibpunct.punctuation['open'])
#         for i, item in enumerate(self.bibitems):
#             frag = self.ownerDocument.createDocumentFragment()
#             frag.append(item.ref)
#             frag.idref = item
#             res.append(frag)
#             res.append(bibpunct.punctuation['sep'])
#         res.pop()
#         res.append(bibpunct.punctuation['close'])
#         return res

#     def citation(self):
#         if bibpunct.punctuation['style'] == 'n':
#             return self.numcitation()
#         elif bibpunct.punctuation['style'] == 's':
#             return self.numcitation()

#         res = []
#         res.append(bibpunct.punctuation['open'] + self.prenote)
#         prevauthor = None
#         prevyear = None
#         duplicateyears = 0
#         previtem = None
#         for i, item in enumerate(self.bibitems):
#             currentauthor = item.citeauthor().textContent
#             currentyear = item.citeyear().textContent

#             # Previous author and year are the same
#             if prevauthor == currentauthor and prevyear == currentyear:
#                 res.pop()
#                 # This is the first duplicate
#                 if duplicateyears == 0:
#                     # Make a reference that points to the same item as
#                     # the first citation in this set.  This will make
#                     # hyperlinked output prettier since the 'a' will 
#                     # be linked to the same place as the reference that
#                     # we just put out.
#                     res.append('')
#                     frag = self.ownerDocument.createDocumentFragment()
#                     frag.append('a')
#                     frag.idref = previtem
#                     res.append(frag)
#                     res.append(bibpunct.punctuation['years'])
#                 else:
#                     res.append(bibpunct.punctuation['years'])
#                 # Create a new fragment with b,c,d... in it
#                 frag = self.ownerDocument.createDocumentFragment()
#                 frag.append(chr(duplicateyears+ord('b')))
#                 frag.idref = item
#                 res.append(frag)
#                 res.append(bibpunct.punctuation['sep']+' ')
#                 duplicateyears += 1

#             # Previous author is the same
#             elif prevauthor == currentauthor:
#                 duplicateyears = 0
#                 res.pop()
#                 res.append(bibpunct.punctuation['years']+' ')
#                 res.append(item.citeyear())
#                 res.append(bibpunct.punctuation['sep']+' ')

#             # Nothing about the previous citation is the same
#             else:
#                 doc = self.ownerDocument
#                 cited = doc.userdata.getPath('bibliography/cited', [])
#                 duplicateyears = 0
#                 if 'longnamesfirst' in PackageOptions and \
#                    item.attributes['key'] not in cited:
#                     cited.append(item.attributes['key'])
#                     doc.userdata.setPath('bibliography/cited', cited)
#                     res.append(item.citealp(full=True))
#                 else:
#                     res.append(item.citealp())
#                 res.append(bibpunct.punctuation['sep']+' ')

#             prevauthor = currentauthor
#             prevyear = currentyear
#             previtem = item

#         res.pop()
#         res.append(self.postnote + bibpunct.punctuation['close'])
#         return res

class citet(NatBibCite):

    def citation(self, full=False, capitalize=False):
        """ Jones et al. (1990) """
        if self.isNumeric():
            return self.numcitation()
        author = self.selectAuthorField(full)
        res = self.ownerDocument.createDocumentFragment()
        i = 0
        for i, item in enumerate(self.bibitems):
            if i == 0 and capitalize:
                res.extend(self.capitalize(item.bibcite.attributes[author]))
            else:
                res.extend(item.bibcite.attributes[author].cloneNode(True))
            res[-1].idref['bibitem'] = item
            res.append(' ')
            res.append(bibpunct.punctuation['open'])
            res.append(self.prenote)
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(bibpunct.punctuation['close'])
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
                res.append(bibpunct.punctuation['close'])
        return res

    def numcitation(self, full=False, capitalize=False):
        """ (1, 2) """
        element = self.ownerDocument.createElement
        orig = res = self.ownerDocument.createDocumentFragment()
        if self.isSuperScript():
            group = element('bgroup')
            orig.append(group)
            res = element('active::^')
            group.append(res)
        i = 0
        res.append(self.prenote)
        res.append(bibpunct.punctuation['open'])
        for i, item in enumerate(self.bibitems):
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
        res.append(bibpunct.punctuation['close'])
        res.append(self.postnote)
        return orig

class citetfull(citet):

    def citation(self):
        """ Jones, Baker, and Williams (1990) """
        return citet.citation(self, full=True)        

class Citet(citet):

    def citation(self):
        return citet.citation(self, capitalize=True)

class citep(NatBibCite):

    def citation(self, full=False, capitalize=False):
        """ (Jones et al., 1990) """
        if self.isNumeric():
            return self.numcitation()
        author = self.selectAuthorField(full)
        res = self.ownerDocument.createDocumentFragment()
        res.append(bibpunct.punctuation['open'])
        res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            if i == 0 and capitalize:
                res.extend(self.capitalize(item.bibcite.attributes[author]))
            else:            
                res.extend(item.bibcite.attributes[author])
            res[-1].idref['bibitem'] = item
            res.append(self.separator+' ')
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
                res.append(bibpunct.punctuation['close'])
        return res

    def numcitation(self):
        """ (1, 2) """
        element = self.ownerDocument.createElement
        orig = res = self.ownerDocument.createDocumentFragment()
        if self.isSuperScript():
            group = element('bgroup')
            orig.append(group)
            res = element('active::^')
            group.append(res)
        res.append(bibpunct.punctuation['open'])
        res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
                res.append(bibpunct.punctuation['close'])
        return orig

class cite(citep, citet):

    def citation(self, full=False, capitalize=False):
        if self.prenote or self.postnote:
            return citep.citation(self, full=full, capitalize=capitalize)
        return citet.citation(self, full=full, capitalize=capitalize)

class Cite(cite):

    def citation(self):
        return cite.citation(self, capitalize=True)

class citepfull(citep):

    def citation(self):
        """ (Jones, Baker, and Williams, 1990) """
        return citep.citation(self, full=True)

class Citep(citep):

    def citation(self):
        return citep.citation(self, capitalize=True)

class citealt(NatBibCite):

    def citation(self, full=False, capitalize=False):
        """ Jones et al. 1990 """
        if self.isNumeric():
            return self.numcitation()
        author = self.selectAuthorField(full)
        res = self.ownerDocument.createDocumentFragment()
        i = 0
        for i, item in enumerate(self.bibitems):
            if i == 0 and capitalize:
                res.extend(self.capitalize(item.bibcite.attributes[author]))
            else:
                res.extend(item.bibcite.attributes[author])
            res[-1].idref['bibitem'] = item
            res.append(' ')
            res.append(self.prenote)
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        return res

    def numcitation(self):
        """ 1, 2 """
        element = self.ownerDocument.createElement
        orig = res = self.ownerDocument.createDocumentFragment()
        if self.isSuperScript():
            group = element('bgroup')
            orig.append(group)
            res = element('active::^')
            group.append(res)
        i = 0
        res.append(self.prenote)
        for i, item in enumerate(self.bibitems):
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        return orig

class citealtfull(citealt):

    def citation(self):
        """ Jones, Baker, and Williams 1990 """
        return citealt.citation(self, full=True)
    
class Citealt(citealt):

    def citation(self):
        return citealt.citation(self, capitalize=True)   

class citealp(NatBibCite):

    def citation(self, full=False, capitalize=False):
        """ Jones et al., 1990 """
        if self.isNumeric():
            return self.numcitation()
        author = self.selectAuthorField(full)
        res = self.ownerDocument.createDocumentFragment()
        res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            if i == 0 and capitalize:
                res.extend(self.capitalize(item.bibcite.attributes[author]))
            else:
                res.extend(item.bibcite.attributes[author])
            res[-1].idref['bibitem'] = item                
            res.append(self.separator+' ')
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        return res

    def numcitation(self):
        """ 1, 2 """
        element = self.ownerDocument.createElement
        orig = res = self.ownerDocument.createDocumentFragment()
        if self.isSuperScript():
            group = element('bgroup')
            orig.append(group)
            res = element('active::^')
            group.append(res)
        res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            res.append(self.citeValue(item))
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
        res.append(self.postnote)
        return orig

class citealpfull(citealp):

    def citation(self):
        """ Jones, Baker, and Williams, 1990 """
        return citealp.citation(self, full=True)

class Citealp(citealp):

    def citation(self):
        return citealp.citation(self, capitalize=True)
        
class citeauthor(NatBibCite):

    def citation(self, full=False, capitalize=False):
        """ Jones et al. """
        if self.isNumeric():
            return
        author = self.selectAuthorField(full)
        res = self.ownerDocument.createDocumentFragment()
        #res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            if i == 0 and capitalize:
                res.extend(self.capitalize(item.bibcite.attributes[author]))
            else:
                res.extend(item.bibcite.attributes[author])
            res[-1].idref['bibitem'] = item                
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        return res

class citeauthorfull(NatBibCite):

    def citation(self):
        """ Jones, Baker, and Williams """
        return citeauthor.citation(self, full=True)

class Citeauthor(citeauthor):
    
    def citation(self):
        return citeauthor.citation(self, capitalize=True)
        
class citeyear(NatBibCite):

    def citation(self):
        """ 1990 """
        if self.isNumeric():
            return
        res = self.ownerDocument.createDocumentFragment()
        #res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            node = item.bibcite.attributes['year'].cloneNode()
            node.idref['bibitem'] = item
            res.append(node)
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        return res

class citeyearpar(NatBibCite):

    def citation(self):
        """ (1990) """
        if self.isNumeric():
            return
        res = self.ownerDocument.createDocumentFragment()
        res.append(bibpunct.punctuation['open'])
        res.append(self.prenote)
        i = 0
        for i, item in enumerate(self.bibitems):
            node = item.bibcite.attributes['year'].cloneNode()
            node.idref['bibitem'] = item
            res.append(node)
            if i < (len(self.bibitems)-1):
                res.append(self.separator+' ')
            else:
                res.append(self.postnote)
        res.append(bibpunct.punctuation['close'])
        return res
    
class citetext(Base.Command):
    args = 'self'
    def digest(self, tokens):
        self.insert(0, bibpunct.punctuation['open'])
        self.append(bibpunct.punctuation['close'])

class defcitealias(Base.Command):
    args = 'key:str text'
    aliases = {}
    def invoke(self, tex):
        res = Base.Command.invoke(self, tex)
        defcitealias.aliases[self.attributes['key']] = self.attributes['text']
        return res

class citetalias(Base.Command):
    args = 'key:str'
    def digest(self, tokens):
        self.extend(defcitealias.aliases[self.attributes['key']])

class citepalias(Base.Command):
    args = 'key:str'
    def digest(self, tokens):
        self.append(bibpunct.punctuation['open'])
        self.extend(defcitealias.aliases[self.attributes['key']])
        self.append(bibpunct.punctuation['close'])

class urlstyle(Base.Command):
    pass