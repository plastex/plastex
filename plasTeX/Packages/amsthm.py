#!/usr/bin/env python

"""

plasTeX.Package.amsthm.py: Partial support for `amsthm.sty` LaTeX Package.

This python package provides support for


* Command: `\\newtheorem`
* Command: `\\newtheoremstyle`
* Command: `\\theoremstyle`
* Environment: `proof`

Keep in mind that when you define and use a new theorem-like environment:

    \\newtheorem{theorem}{Theorem}
    \\begin{theorem}[Euclid's] This is a Theorem.
    \\end{theorem}

this package translates the above construction to simplified LaTeX code (as opposed to a `theorem` environment that can be styled throught the renderer.)

I chose this instead of relying on the renderer because the user can specify everything, from the names to the header fonts, to the colors, to the body font, etc. I don't think the rendering mechanism can cope with environments of user defined names and user defined styles.

It supports the starred version (without numbers) of `\\newtheorem`

This package keeps a list of user defined styles in the `userdata` space under `packages/amsthm/styles`. This userdata is prepopulated with (a simplified version of) the  default styles in amsthm.sty: plain, remark, and definition.

It also keeps a list of theorem-like environments under `packages/amsthm/theorems`.

Detailed support:

1. `\\newtheorem * {name}[shared counter]{Header}[reset by]` is supported. It creates an environment `\\begin{name}[optional note] .. \\end{name}`, which translates on invocation into simpler LaTeX.

2. `\\newtheoremstyle {name} {above space} {below space} {main body font} {indent amount} {header font} {punctuation hafter head} {space between head and body} {header spec}` is partially supported---it currently ignores everything but main body font and header font. The header spec is hardcoded and equivalent to `\\thmname{#1}\\thmnumber{ #2}\\thmnote{ (3)}`. Read the `amsthm` manual for more information on defining theorem styles. There's a list of defined styles in `userdata` space, in `packages/amsthm/styles`.

3. `\\theoremstyle{name}` Set the current theorem style to `name`. Not checked for errors.

4 `\\begin{proof} .. \\end{proof}` Translated into simpler LaTeX.

5. `\\swapnumbers`  Ignored & Unsupported.

TODO & NOT FULLY WORKING:

1. I can't get `\\label` to  reference properly the correct statement.


2. For some reason, I can't get

        \\newtheorem{theorem}{Theorem}
        \\begin{theorem} Statement \\end{theorem}

    to wrap the Statement in a span. Currently it gives you something like:

        <p><b>Theorem 1</b> <i>Statement</i><p>

    and I would like something like:

        <span class="statement"><p><b>Theorem 1</b> <i>Statement</i><p></span>

3. Support of `header spec`.


Example document:

    \\documentclass{article}
    \\usepackage{amsthm}
    \\usepackage{color}

    \\newtheoremstyle{redPlain}  {\\bigskipamount}
                                {\\bigskipamount}
                                {\\itshape}
                                {}
                                {\\color[cmyk]{0,1.00,0.65,0.34}\\bfseries}
                                {:}
                                {1em}
                                {\\thmname{#1}\\thmnumber{ #2}\\thmnote{ (#3)}}
    \\theoremstyle{redPlain}
    \\newtheorem*{starred}{Starred}
    \\newtheorem{normal}{Normal}
    \\newtheorem{normalshared}[normal]{Normal And Shared}
    \\theoremstyle{plain}
    \\newtheorem{within}{Within}[section]
    \\newtheorem{withinshared}[within]{Within And Shared}
    \\begin{document}

    \\section{A section}
    \\begin{starred}[Note]
        An starred theorem
    \\end{starred}
    \\begin{normal}
        A normal theorem
    \\end{normal}
    \\begin{normalshared}[Note]
        A normal theorem, with shared counter.
    \\end{normalshared}
    \\begin{within}
        A theorem numbered within sections
    \\end{within}
    \\begin{withinshared}[Note]
        A theorem with counter shared with a theorem numbered within sections
    \\end{withinshared}
    \\section{Another section}
    \\begin{starred}
        An starred theorem
    \\end{starred}
    \\begin{normal}
        A normal theorem
    \\end{normal}
    \\begin{normalshared}
        A normal theorem, with shared counter.
    \\end{normalshared}
    \\begin{within}
        A theorem numbered within sections
    \\end{within}
    \\begin{withinshared}\\label{T:1}
        A theorem with counter shared with a theorem numbered within sections
    \\end{withinshared}
    \\end{document}


"""

import plasTeX


class swapnumbers(plasTeX.Command):
    pass


def ProcessOptions(options, document):
    context = document.context
    context.newenvironment("proof", 1, 
        u"\\par\\noindent{\\normalfont\\itshape #1.}\\enspace",
        None, opt = u"\\proofname")
    document.userdata.setPath('packages/amsthm/styles',{
        'plain' : {
            'name': 'plain',
            'above': u"0pt",
            'below': u"0pt",
            'bodyfont': u"\\itshape",
            'indentamount': u'0pt',
            'headfont': u"\\bfseries",
            'punctuation': u".",
            'between': u' ',
            'headspec': None
        },
        'definition' : {
            'name': 'definition',
            'above': u"0pt",
            'below': u"0pt",
            'bodyfont': u"",
            'indentamount': u'0pt',
            'headfont': u"\\bfseries",
            'punctuation': u".",
            'between': u' ',
            'headspec': None
        },
        'remark' : {
            'name': u'remark',
            'above': u'0pt',
            'below': u'0pt',
            'bodyfont': u"",
            'indentamount': '0pt',
            'headfont': u"\\bfseries",
            'punctuation': u".",
            'between': u' ',
            'headspec': None
        },

    })
    document.userdata.setPath('packages/amsthm/theorems',[])
    document.userdata.setPath('packages/amsthm/currentstyle', 'plain')



class theoremstyle(plasTeX.Command):
    args = 'style:str'
    def invoke(self, tex):
        self.parse(tex)
        self.ownerDocument.userdata.setPath('packages/amsthm/currentstyle', self.attributes['style'])


class newtheoremstyle(plasTeX.Command):
    args = 'name above below bodyfont indentamount headfont punctuation between headspec'
    def invoke(self, tex):
        self.parse(tex)
        d = self.ownerDocument.userdata.getPath("packages/amsthm/styles")
        s = {}
        for k, v in self.attributes.items():
            s[str(k)]=tex.source(v)
        d[tex.source(self.attributes['name'])] = s


class newtheorem(plasTeX.Command):
    args = ' * name:str [ shared:str ] header:str [ parent:str] '
    
    def invoke(self, tex):
        self.parse(tex)
        a = self.attributes
        name = str(a['name'])
        header = a['header']
        star = a['*modifier*'] == '*'
        parent = a['parent']
        shared = a['shared']
        style = self.ownerDocument.userdata.getPath('packages/amsthm/currentstyle')

        l = self.ownerDocument.userdata.getPath('packages/amsthm/theorems')
        l += [name]


        if star:
            thecounter = None
        else:
            if parent and not shared:
                self.ownerDocument.context.newcounter(name, initial=0, resetby=parent)
                self.ownerDocument.context.newcommand("the"+name, 0,
                                        "\\arabic{%s}.\\arabic{%s}"%(parent,name))
                thecounter = name
            elif shared:
                thecounter = shared
            else:
                thecounter = name
                self.ownerDocument.context.newcounter(name, initial=0)
                self.ownerDocument.context.newcommand("the"+name, 0, "\\arabic{%s}" %name)

        data = {
                'macroName': name,
                'counter': thecounter,
                'thehead': header,
                'thename': name,
                'labelable': True,
                'forcePars': True,
                'thestyle': style
            }
        th = type(name, (theoremCommand,), data)
        self.ownerDocument.context.addGlobal(name, th)


class theoremCommand(plasTeX.Environment):
    args = '[ note:chr ]'
    blockType = True
    
    def invoke(self, tex):
        # self.style['class'] = u'amsthm '+self.thename
        if self.macroMode == self.MODE_BEGIN:
            note = tex.readArgument('[]')
            
            if note:
                note = tex.source(note)
                
            if self.counter:
# Done automagically:  self.ownerDocument.context.counters[self.counter].stepcounter()
                self.ownerDocument.context.currentlabel = self
                self.style['id'] = self.id

            style_dict = self.ownerDocument.userdata.getPath(
                "packages/amsthm/styles/"+self.thestyle
            )
            head_style = style_dict['headfont']
            note_opener = u'('
            note_closer = u')'
            punctuation = style_dict['punctuation'] if style_dict['punctuation'] else u"."
            body_style = style_dict['bodyfont']
            # between = style_dict['between']
            between = u' '

            s = u'{'+head_style+u"{}"+self.thehead

            if self.counter:
                s += u'~\\the'+self.counter

            if note:
                s += u'{} ' + note_opener + note + note_closer

            s += punctuation+between+'}'+body_style
            self.ownerDocument.context.push(self)
            tex.input(s)
            super(theoremCommand, self).invoke(tex)
            
        elif self.macroMode == self.MODE_END:
            self.ownerDocument.context.pop(self)
            return

