#!/usr/bin/env python

"""
natbib

TODO: 
    - superscript style
    - sort&compress (sort works, compress doesn't)

"""

import string, plasTeX
from plasTeX import TeXFragment
from plasTeX import Base

log = plasTeX.Logging.getLogger()

PackageOptions = {}

def ProcessOptions(options):
    """ Process package options """
    if options is None:
        return
    PackageOptions.update(options)
    for key, value in options.items():
        if key == 'numbers':
            bibpunct.punctuation['style'] = 'n'
            ProcessOptions({'square':True, 'comma':True})
        elif key == 'super':
            bibpunct.punctuation['style'] = 's'
            bibpunct.punctuation['open'] = ''
            bibpunct.punctuation['close'] = ''
        elif key == 'authoryear':
            ProcessOptions({'round':True, 'colon':True})
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

class bibstyle(Base.Command):
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
            s = bibstyle.styles[self.attributes['style']]
        except KeyError:
            log.warning('Could not find bibstyle: "%s"',
                         self.attributes['style'])
            return res
        p = bibpunct.punctuation
        p['post']  = s[0]
        p['open']  = s[1]
        p['close'] = s[2]
        p['sep']   = s[3]
        p['style'] = s[4]
        p['dates'] = s[5]
        p['years'] = s[6]
        return res    

class bibpunct(Base.Command):
    """ Set up punctuation of citations """
    args = '[ post:str ] open:str close:str sep:str ' + \
           'style:str dates:str years:str'
    punctuation = {'post':', ', 'open':'(', 'close':')', 'sep':';', 
                   'style':'a', 'dates':',', 'years':','}

    def invoke(self, tex):
        res = Base.Command(self, tex)
        for key, value in self.attributes.items():
            if value is not None:
                bibpunct.punctuation[key] = value.textContent            
        return res

class bibcite(Base.Command):
    """ Auxiliary file information """
    citations = {}
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
        self.citations[self.attributes['key']] = value

class thebibliography(Base.thebibliography):

    class bibitem(Base.thebibliography.bibitem):
        cited = []

        def citation(self):
            try: 
                return bibcite.citations[self.attributes['key']]
            except KeyError, msg:
                pass
            # We don't have a citation that matches, fill the fields
            # with dummy data
            value = Base.Command()
            value.append('??')
            for item in ['year','author','fullauthor']:
                obj = Base.Command()
                obj.append('??')
                value.attributes[item] = obj
            return value
        citation = property(citation)

        def cite(self):
            """ Jones et al. (1990) """
            if 'longnamesfirst' in PackageOptions and \
               self.attributes['key'] not in self.cited:
                full = True
                self.cited.append(self.attributes['key'])
            if bibpunct.punctuation['style'] == 's':
                return self.citep(full=full)
            elif bibpunct.punctuation['style'] == 'n':
                return self.citep(full=full)
            return self.citet(full=full)
    
        def citep(self, full=False):
            """ (Jones et al., 1990) """
            res = TeXFragment()
            res.append(bibpunct.punctuation['open'])
            if bibpunct.punctuation['style'] == 's':
                res.extend(self.ref)
            elif bibpunct.punctuation['style'] == 'n':
                res.extend(self.ref)
            else:
                res.extend(self.citealp(full=full))
            res.append(bibpunct.punctuation['close'])
            res.idref = self
            return res
    
        def citepfull(self):
            """ (Jones, Baker, and Williams, 1990) """
            return self.citep(full=True)
        
        def citet(self, full=False):
            """ Jones et al. (1990) """
            if 'longnamesfirst' in PackageOptions and \
               self.attributes['key'] not in self.cited:
                full = True
                self.cited.append(self.attributes['key'])
            if full: which = 'fullauthor'
            else: which = 'author'
            res = TeXFragment()
            res.extend(self.citation.attributes[which])
            res.append(' ')
            res.append(bibpunct.punctuation['open'])
            if bibpunct.punctuation['style'] == 's':
                res.extend(self.ref)
            elif bibpunct.punctuation['style'] == 'n':
                res.extend(self.ref)
            else:
                res.extend(self.citation.attributes['year'])
            res.append(bibpunct.punctuation['close'])
            res.idref = self
            return res
    
        def citetfull(self):
            """ Jones, Baker, and Williams (1990) """
            return self.citet(full=True)
        
        def citealt(self, full=False):
            """ Jones et al. 1990 """
            if full: which = 'fullauthor'
            else: which = 'author'
            res = TeXFragment()
            res.extend(self.citation.attributes[which])
            res.append(' ')
            res.extend(self.citation.attributes['year'])
            res.idref = self
            return res
    
        def citealtfull(self):
            """ Jones, Baker, and Williams 1990 """
            return self.citealt(full=True)
        
        def citealp(self, full=False):
            """ Jones et al., 1990 """
            if full: which = 'fullauthor'
            else: which = 'author'
            res = TeXFragment()
            res.extend(self.citation.attributes[which])
            res.append(bibpunct.punctuation['dates'])
            res.append(' ')
            res.extend(self.citation.attributes['year'])
            res.idref = self
            return res
    
        def citealpfull(self):
            """ Jones, Baker, and Williams, 1990 """
            return self.citealp(full=True)
        
        def citeauthor(self, full=False):
            """ Jones et al. """
            if full: which = 'fullauthor'
            else: which = 'author'
            res = TeXFragment()
            res.extend(self.citation.attributes[which])
            res.idref = self
            return res
    
        def citeauthorfull(self):
            """ Jones, Baker, and Williams """
            return self.citeauthor(full=True)
        
        def citeyear(self):
            """ 1990 """
            return self.citation.attributes['year']
    
        def citeyearpar(self):
            """ (1990) """
            res = TeXFragment()
            res.append(bibpunct.punctuation['open'])
            res.extend(self.citeyear())
            res.append(bibpunct.punctuation['close'])
            res.idref = self
            return res
    
        def Citet(self):
            node = self.citet().cloneNode(True)
            if node.firstChild.nodeType == Base.Command.TEXT_NODE:
                node[0] = node[0].capitalize()
            else:
                node[0][0] = node[0][0].capitalize()
            node.idref = self
            return node
    
        def Citep(self):
            res = TeXFragment()
            res.append(bibpunct.punctuation['open'])
            node = self.citealp().cloneNode(True)
            if node.firstChild.nodeType == Base.Command.TEXT_NODE:
                node[0] = node[0].capitalize()
            else:
                node[0][0] = node[0][0].capitalize()
            res.append(node)
            res.append(bibpunct.punctuation['close'])
            res.idref = self
            return res
    
        def Citeauthor(self):
            node = self.citeauthor().cloneNode(True)
            if node.firstChild.nodeType == Base.Command.TEXT_NODE:
                node[0] = node[0].capitalize()
            else:
                node[0][0] = node[0][0].capitalize()
            node.idref = self
            return node
    
class harvarditem(thebibliography.bibitem):
    args = '[ abbrlabel ] label year key:str'

class NatBibCite(Base.cite):
    """ Base class for all natbib-style cite commands """
    args = '* [ text ] [ text2 ] keys:list:str'
    citemethod = thebibliography.bibitem.cite

    def bibitems(self):
        items = super(NatBibCite, self).bibitems
        if PackageOptions.has_key('sort') or \
           PackageOptions.has_key('sort&compress') or \
           PackageOptions.has_key('sortandcompress'):
            items.sort(lambda x, y: int(x.ref) - int(y.ref))
        return items
    bibitems = property(bibitems)

    def prenote(self):
        """ Text that comes before the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            out = TeXFragment()
            out.extend(a['text'])
            out.append(' ')
            return out
        return ''
    prenote = property(prenote)

    def postnote(self):
        """ Text that comes after the citation """
        a = self.attributes
        if a.get('text2') is not None and a.get('text') is not None:
            out = TeXFragment()
            out.append(bibpunct.punctuation['post'])
            out.extend(a['text2'])
            return out
        elif a.get('text') is not None:
            out = TeXFragment()
            out.append(bibpunct.punctuation['post'])
            out.extend(a['text'])
            return out
        return ''
    postnote = property(postnote)

    def citation(self):
        """
        Return the citation in pieces fit for rendering

        This method returns a list containing the prenote, postnote,
        delimiters and the citation content.  The list will always
        have a length that is odd, where the even items are plain
        text (i.e. prenote, postnote, and delimiters) and the even 
        items are the TeX fragments that hold the citation text
        (which can be rendered as hyperlinks).

        """
        res = []
        res.append(self.prenote)
        for item in self.bibitems:
            out = self.citemethod(item)
            out.idref = item
            res.append(out)
            res.append(bibpunct.punctuation['sep']+' ')
        res.pop()
        res.append(self.postnote)
        return res
            
class NatBibCiteNoOptional(NatBibCite):
    args = '* keys:list:str'

class citep(NatBibCite):

    def numcitation(self):
        """ Numeric style citations """
        res = []
        res.append(bibpunct.punctuation['open'])
        for i, item in enumerate(self.bibitems):
            frag = TeXFragment()
            frag.append(item.ref)
            frag.idref = item
            res.append(frag)
            res.append(bibpunct.punctuation['sep'])
        res.pop()
        res.append(bibpunct.punctuation['close'])
        return res

    def citation(self):
        if bibpunct.punctuation['style'] == 'n':
            return self.numcitation()
        elif bibpunct.punctuation['style'] == 's':
            return self.numcitation()

        res = []
        res.append(bibpunct.punctuation['open'] + self.prenote)
        prevauthor = None
        prevyear = None
        duplicateyears = 0
        previtem = None
        for i, item in enumerate(self.bibitems):
            currentauthor = item.citeauthor().textContent
            currentyear = item.citeyear().textContent

            # Previous author and year are the same
            if prevauthor == currentauthor and prevyear == currentyear:
                res.pop()
                # This is the first duplicate
                if duplicateyears == 0:
                    # Make a reference that points to the same item as
                    # the first citation in this set.  This will make
                    # hyperlinked output prettier since the 'a' will 
                    # be linked to the same place as the reference that
                    # we just put out.
                    res.append('')
                    frag = TeXFragment()
                    frag.append('a')
                    frag.idref = previtem
                    res.append(frag)
                    res.append(bibpunct.punctuation['years'])
                else:
                    res.append(bibpunct.punctuation['years'])
                # Create a new fragment with b,c,d... in it
                frag = TeXFragment()
                frag.append(chr(duplicateyears+ord('b')))
                frag.idref = item
                res.append(frag)
                res.append(bibpunct.punctuation['sep']+' ')
                duplicateyears += 1

            # Previous author is the same
            elif prevauthor == currentauthor:
                duplicateyears = 0
                res.pop()
                res.append(bibpunct.punctuation['years']+' ')
                res.append(item.citeyear())
                res.append(bibpunct.punctuation['sep']+' ')

            # Nothing about the previous citation is the same
            else:
                duplicateyears = 0
                if 'longnamesfirst' in PackageOptions and \
                   item.attributes['key'] not in item.cited:
                    item.cited.append(item.attributes['key'])
                    res.append(item.citealp(full=True))
                else:
                    res.append(item.citealp())
                res.append(bibpunct.punctuation['sep']+' ')

            prevauthor = currentauthor
            prevyear = currentyear
            previtem = item

        res.pop()
        res.append(self.postnote + bibpunct.punctuation['close'])
        return res

class citet(NatBibCite):
    citemethod = thebibliography.bibitem.citet

class citealt(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.citealt

class citealp(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.citealp

class citeauthor(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.citeauthor

class citeyear(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.citeyear

class citeyearpar(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.citeyearpar

class Citet(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.Citet

class Citep(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.Citep

class Citeauthor(NatBibCiteNoOptional):
    citemethod = thebibliography.bibitem.Citeauthor

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
