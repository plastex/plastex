#!/usr/bin/env python

from plasTeX.Renderers import Renderer as BaseRenderer
import textwrap, re, string

class ManPageRenderer(BaseRenderer):
    """ Renderer for UNIX man pages """

    outputType = unicode
    fileExtension = '.man'
    
    aliases = {
        'superscript': 'active::^',
        'subscript': 'active::_',
        'dollar': '$',
        'percent': '%',
        'opencurly': '{',
        'closecurly': '}',
        'underscore': '_',
        'ampersand': '&',
        'hashmark': '#',
        'space': ' ',
        'tilde': 'active::~',
        'at': '@',
        'backslash': '\\',
    }
    
    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        
        # Load dictionary with methods
        for key in vars(type(self)):
            if key.startswith('do__'):
                self[self.aliases[key[4:]]] = getattr(self, key)
            elif key.startswith('do_'):
                self[key[3:]] = getattr(self, key)

        self['default-layout'] = self['document-layout'] = self.default
        
        self.footnotes = []
        self.blocks = []

    def default(self, node):
        """ Rendering method for all non-text nodes """
        # Handle characters like \&, \$, \%, etc.
        if len(node.nodeName) == 1 and node.nodeName not in string.letters:
            return self.textDefault(node.nodeName)
            
        # Render child nodes
        return unicode(node)

    def textDefault(self, node):
        return unicode(node)

    def processFileContent(self, document, s):
        s = BaseRenderer.processFileContent(self, document, s)

        # Clean up newlines
        s = re.sub(r'\s*\n(\s*\n)+', r'\n\n', s)
        s = re.sub(r'(\s*\n)+(\.B[ld])', r'\n\2', s)
        s = re.sub(r'(\.E[ld])\s*(\.B[ld])', r'\1\n\n\2', s)
        s = re.sub(r'\.Ed\s*\.Bd', r'.Ed\n.Bd', s)
        s = s.lstrip()
        
        return s
    
    # Alignment

    def do_flushleft(self, node):
        return u'\n.Bd -ragged\n%s\n.Ed\n' % node
        
    do_raggedbottom = do_raggedright = do_leftline = do_flushleft
    
    def center(self, text):
        return u'\n.Bd -centered\n%s\n.Ed\n' % text
            
    def do_center(self, node):
        return self.center(unicode(node))
        
    do_centering = do_centerline = do_center

    def do_flushright(self, node):
        return u'\n.Bd -offset right\n%s\n.Ed\n' % node
        
    do_raggedleft = do_llap = do_flushright
    
    # Arrays
    
    def do_array(self, node, render=unicode):
        output = ['.TS']

        # Process colspecs
        if node.colspec:
            alignments = [x.style['text-align'] for x in node.colspec]
        else:
            alignments = ['l']*100
        for row in node:
            colspec = []
            for i, cell in enumerate(row):
                colspec.append(cell.style.get('text-align', alignments[i])[0])
            output.append(' '.join(colspec))
        output[-1] += '.'

        # Render table
        for row in node:
            content = []
            for cell in row:
                content.append(render(cell).strip())
            output.append('\t'.join(content))
        output.append('.TE')
        output.append('')

        return re.sub(r'\s*.TE\s*', r'\n.TE\n', u'\n'.join(output))
        
    do_tabular = do_tabularx = do_longtable = do_array
    
    def do_cline(self, node):
        return ''
        
    def do_multicolumn(self, node):
        return unicode(node)

    # Bibliography
    def do_thebibliography(self, node):
        output = ['','.Sh Bibliography','']
        output.append('.Bl -tag -width indent')
        for item in node:
            output.append('.It %s' % unicode(item.bibcite).strip())
            output.append(unicode(item).strip())
        output.append('.El')
        output.append('')
        return u'\n'.join(output)        

    def do_bibliographystyle(self, node):
        return u''

    def do_bibliography(self, node):
        return self.default(node)
  
    def do_cite(self, node):
        output = []
        for item in node.citation():
            output.append(unicode(item))
        return u''.join(output)

    def do_bibliographyref(self, node):
        return self.default(node)

    # Boxes
    
    do_mbax = do_makebox = do_fbox = do_framebox = do_parbox = default
    do_minipage = do_raisebox = do_rule = default
    
    # Breaking
    
    def do_linebreak(self, node):
        return u'\n\n'
        
    do_newline = do_pagebreak = do_newpage = do_clearpage = do_cleardoublepage = do_linebreak

    # Crossref
    
    def do_ref(self, node):
        return unicode(node.idref['label'].ref)

    def do_pageref(self, node):
        return u'*'

    def do_label(self, node):
        return u''

    # Floats
    
    def do_figure(self, node):
        return unicode(node)
        
    do_table = do_marginpar = do_figure

    def do_caption(self, node):
        return u'\n%s %s: %s\n' % (node.title, node.ref, unicode(node).strip())

    # Font Selection
    
    do_sffamily = do_textsf = default
    do_upshape = do_textup = default
    do_scshape = do_textsc = default
    do_sc = default
    do_tiny = do_scriptsize = do_footnotesize = do_small = default
    do_normalsize = do_large = do_Large = do_LARGE = do_huge = do_HUGE = default

    def do_textbf(self, node):
        return u'\\fB%s\\fP' % node

    do_bfseries = do_bf = do_textbf

    def do_textit(self, node):
        return u'\\fI%s\\fP' % node
        
    do_itshape = do_it = do_slshape = do_textsl = do_sl = do_cal = do_textit
    
    def do_texttt(self, node):
        return u'\\fC%s\\fP' % node
    
    do_ttfamily = do_tt = do_texttt

    def do_textmd(self, node):
        return u'\\fR%s\\fP' % node
    
    do_mdseries = do_rmfamily = do_textrm = do_textnormal = do_rm = do_textmd

    def do_symbol(self, node):
        return u'*'

    # Footnotes
    def do_footnote(self, node):
        mark = u'[%s]' % (len(self.footnotes)+1)
        self.footnotes.append(unicode(node))
        return mark
        
    def do_footnotetext(self, node):
        self.do_footnote(self, node)
        return ''
    
    def do_footnotemark(self, node):
        return u'[%s]' % (len(self.footnotes)+1)
    
    # Index
    
    def do_theindex(self, node):
        return u''
        
    do_printindex = do_index = do_theindex
    
    # Lists

    def do_itemize(self, node):
        output =['','.Bl -bullet -offset 3n -compact']
        for item in node:
            output.append('.It')
            output.append(unicode(item).strip())
        output.append('.El')
        output.append('')
        return u'\n'.join(output)        
        
    def do_enumerate(self, node):
        output = ['','.Bl -enum -offset 3n -compact']
        for item in node:
            output.append('.It')
            output.append(unicode(item).strip())
        output.append('.El')
        output.append('')
        return u'\n'.join(output)        
        
    def do_description(self, node):
        output = ['','.Bl -tag -width 3n']
        for item in node:
            output.append('.It %s' % unicode(item.attributes.get('term','')).strip())
            output.append(unicode(item).strip())
        output.append('.El')
        output.append('')
        return u'\n'.join(output)        

    do_list = do_trivlist = do_description
    
    # Math
    
    def do_math(self, node):
        return re.sub(r'\s*(_|\^)\s*', r'\1', node.source.replace('\\','\\\\'))

    do_ensuremath = do_math
    
    def do_equation(self, node):
        s = u'   %s' % re.compile(r'^\s*\S+\s*(.*?)\s*\S+\s*$', re.S).sub(r'\1', node.source.replace('\\','\\\\'))
        return re.sub(r'\s*(_|\^)\s*', r'\1', s)

    do_displaymath = do_equation
    
    def do_eqnarray(self, node):
        def render(node):
            s = re.compile(r'^\$\\\\displaystyle\s*(.*?)\s*\$\s*$', re.S).sub(r'\1', node.source.replace('\\','\\\\'))
            return re.sub(r'\s*(_|\^)\s*', r'\1', s)
        return self.do_array(node, render=render)

    do_align = do_gather = do_falign = do_multiline = do_eqnarray 
    do_multline = do_alignat = do_split = do_eqnarray
    
    # Misc
    
    do_bgroup = default
    
    def do_def(self, node):
        return u''
    
    do_tableofcontents = do_input = do_protect = do_let = do_def
    do_newcommand = do_hfill = do_hline = do_openout = do_renewcommand = do_def
    do_write = do_hspace = do_appendix = do_global = do_noindent = do_def
    do_include = do_markboth = do_setcounter = do_refstepcounter = do_def
    do_medskip = do_smallskip = do_parindent = do_indent = do_setlength = do_def
    do_settowidth = do_addtolength = do_nopagebreak = do_newwrite = do_def
    do_newcounter = do_typeout = do_sloppypar = do_hfil = do_thispagestyle = do_def

    def do_egroup(self, node):
        return u''
    
    # Pictures
    
    def do_picture(self, node):
        return u''
        
    # Primitives
    
    def do_par(self, node):
        return u'\n%s\n' % unicode(node).strip()

    def do__superscript(self, node):
        return self.default(node)
    
    def do__subscript(self, node):
        return self.default(node)
    
    # Quotations
     
    def do_quote(self, node):
        backslash = self['\\']
        self['\\'] = lambda *args: u'\001'
        res = [x.strip() for x in unicode(node).split(u'\001')]
        output = []
        for par in [x.strip() for x in unicode(node).split(u'\n\n')]:
            for item in [x.strip() for x in par.split(u'\001')]:
                output.append(self.fill(item, initial_indent='   ', subsequent_indent='      '))
            output.append('')
        output.pop()
        self['\\'] = backslash
        return u'\n'.join(output)
    
    do_quotation = do_verse = do_quote

    # Sectioning

    def do_document(self, node):
        content = unicode(node).rstrip()
        footnotes = ''
        if self.footnotes:
            output = ['','.Bl -tag -offset indent']
            for i, item in enumerate(self.footnotes):
                output.append('.It [%s]' % (i+1))
                output.append(item)
            output.append('.El')
            output.append('')
            footnotes = '\n'.join(output)
        return u'%s%s' % (content, footnotes)
        
    def do_maketitle(self, node):
        output = []
        metadata = node.ownerDocument.userdata
        if 'date' in metadata:
            output.append('.Dd %s' % metadata['date'])
        if 'title' in metadata:
            output.append('.Dt %s' % unicode(metadata['title']).upper())
        output.append('')
        return u'\n'.join(output)

    def do_section(self, node):
        return u'.Sh %s\n%s' % (node.title, node)

    do_part = do_chapter = do_section

    def do_subsection(self, node):
        return u'.Ss %s\n%s' % (node.title, node)

    do_subsubsection = do_paragraph = do_subparagraph = do_subsubparagraph = do_subsection

    def do_title(self, node):
        return u''
        
    do_author = do_date = do_thanks = do_title
    
    def do_abstract(self, node):
        return self.center(unicode(node).strip())

    # Sentences

    def do__dollar(self, node):
        return u'$'
        
    def do__percent(self, node):
        return u'%'
        
    def do__opencurly(self, node):
        return u'{'
        
    def do__closecurly(self, node):
        return u'}'
    
    def do__underscore(self, node):
        return u'_'
        
    def do__ampersand(self, node):
        return u'&'
        
    def do__hashmark(self, node):
        return u'#'
    
    def do__space(self, node):
        return u' '

    def do_LaTeX(self, node):
        return u'LaTeX'

    def do_TeX(self, node):
        return u'TeX'

    def do_emph(self, node):
        return self.default(node)
        
    do_em = do_emph

    def do__tilde(self, node):
        return u' '

    def do_enspace(self, node):
        return u' '

    do_quad = do_qquad = do_enspace
        
    def do_enskip(self, node):
        return u''

    do_thinspace = do_enskip

    def do_underbar(self, node):
        return self.default(node)

    # Space
    
    def do_hspace(self, node):
        return u' '
    
    def do_vspace(self, node):
        return u''
        
    do_bigskip = do_medskip = do_smallskip = do_vspace
    
    # Tabbing - not implemented yet
    
    # Verbatim
    
    def do_verbatim(self, node):
        return u'\n.Bd -literal%s.Ed\n' % node

    do_alltt = do_verbatim

    def do_mbox(self, node):
        return self.default(node)

    def do__at(self, node):
        return u''

    def do__backslash(self, node):
        return u'\\'

Renderer = ManPageRenderer
