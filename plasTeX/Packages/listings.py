import sys, re
from pathlib import Path
from typing import Optional

from plasTeX import VerbatimEnvironment, Environment, Command
from plasTeX.Base.TeX.Text import bgroup
from plasTeX.PackageResource import PackagePreCleanupCB, PackageCss

try:
    import pygments
    from pygments import lexers
    from pygments.formatters import HtmlFormatter
except:
    pygments = None

class listingsname(Command):
    str = 'Listing'

def ProcessOptions(options, document):
    document.context.newcounter('listings',
                                resetby='chapter',
                                format='${thechapter}.${listings}')
    document.userdata['listings'] = options
    if pygments:
        cb = PackagePreCleanupCB(renderers='html5', data=make_pygments_css)
        css = PackageCss(renderers='html5', path=Path('pygments.css'))
        css.copy = False
        document.addPackageResource([cb, css])

def make_pygments_css(document):
    path = Path('styles')/'pygments.css'
    path.write_text(HtmlFormatter().get_style_defs())
    return [str(path)]

class lstset(Command):
    args = 'arguments:dict'
    def invoke(self, tex):
        Command.invoke(self, tex)
        if 'language' in self.attributes['arguments']:
            self.ownerDocument.context.current_language = \
                self.attributes['arguments']['language']

class lstlisting(VerbatimEnvironment):
    args = '[ arguments:dict ]'
    counter = 'listings'

    def invoke(self, tex):
        """
        We enter verbatim mode by setting all category codes to CC_LETTER
        or CC_OTHER. However, we will have to manually scan for the end of the
        environment since the tokenizer does not tokenize the end of the
        environment as an EscapeSequence Token.
        This is almost the same code as in VerbatimEnvironment, but
        we need to first try to parse the optional argument.
        """
        if self.macroMode == Environment.MODE_END:
            return

        escape = self.ownerDocument.context.categories[0][0]
        bgroup = self.ownerDocument.context.categories[1][0]
        egroup = self.ownerDocument.context.categories[2][0]
        self.ownerDocument.context.push(self)
        tokenizer = tex.inputs[0][0]
        next_token = next(tex.inputs[0][1])
        if next_token == '[':
            tokenizer.pushToken(next_token)
            self.parse(tex)
        else:
            tokenizer.pushToken(next_token)
            self.attributes['arguments'] = None
        self.ownerDocument.context.setVerbatimCatcodes()
        tokens = [self]

        # Get the name of the currently expanding environment
        name = self.nodeName
        if self.macroMode != Environment.MODE_NONE:
            if self.ownerDocument.context.currenvir is not None:
                name = self.ownerDocument.context.currenvir

        # If we were invoked by a \begin{...} look for an \end{...}
        endpattern = list(r'%send%s%s%s' % (escape, bgroup, name, egroup))

        # If we were invoked as a command (i.e. \verbatim) look
        # for an end without groupings (i.e. \endverbatim)
        endpattern2 = list(r'%send%s' % (escape, name))

        endlength = len(endpattern)
        endlength2 = len(endpattern2)
        # Iterate through tokens until the endpattern is found
        for tok in tex:
            tokens.append(tok)
            if len(tokens) >= endlength:
                if tokens[-endlength:] == endpattern:
                    tokens = tokens[:-endlength]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break
            if len(tokens) >= endlength2:
                if tokens[-endlength2:] == endpattern2:
                    tokens = tokens[:-endlength2]
                    self.ownerDocument.context.pop(self)
                    # Expand the end of the macro
                    end = self.ownerDocument.createElement(name)
                    end.parentNode = self.parentNode
                    end.macroMode = Environment.MODE_END
                    res = end.invoke(tex)
                    if res is None:
                        res = [end]
                    tex.pushTokens(res)
                    break

        return tokens

    def digest(self, tokens):
        VerbatimEnvironment.digest(self, tokens)
        args = self.attributes.get('arguments') or dict()
        _format(self, self.textContent.strip(), wrap=True,
                language=args.get('language'))


class endlstlisting(lstlisting):
    def invoke(self, tex):
        end = self.ownerDocument.createElement(self.nodeName[3:])
        end.parentNode = self.parentNode
        end.macroMode = Environment.MODE_END
        return [end]


class lstinline(Command):
    args = '[ arguments:dict ]'

    def invoke(self, tex):
        """ Parse for matching delimiters after trying to parse the optional argument"""
        self.ownerDocument.context.push(self)
        tokenizer = tex.inputs[0][0]
        next_token = next(tex.inputs[0][1])
        if next_token == '[':
            tokenizer.pushToken(next_token)
            self.parse(tex)
        else:
            tokenizer.pushToken(next_token)
            self.attributes['arguments'] = None
        self.ownerDocument.context.setVerbatimCatcodes()

        # See what the delimiter is
        endpattern = next(iter(tex))
        self.delimiter = endpattern
        if isinstance(endpattern, bgroup):
            self.delimiter = endpattern = Other('}')
        tokens = [self, endpattern]
        # Parse until this delimiter is seen again
        for tok in tex:
            tokens.append(tok)
            if tok == endpattern:
                break
        self.ownerDocument.context.pop(self)
        return tokens

    def digest(self, tokens):
        endpattern = next(iter(tokens))
        for tok in tokens:
            if tok == endpattern:
                break
            self.appendChild(tok)
        args = self.attributes.get('arguments') or dict()
        _format(self, self.textContent, wrap=False,
                language=args.get('language'))


class lstinputlisting(Command):
    args = '[ arguments:dict ] file:str'
    counter = 'listings'

    def invoke(self, tex):
        Command.invoke(self, tex)
        if 'file' not in list(self.attributes.keys()) or not self.attributes['file']:
            raise ValueError('Malformed \\lstinputlisting macro.')
        encoding = self.config['files']['input-encoding']
        _format(self, open(self.attributes['file'],  encoding=encoding), wrap=True)

def _format(self, file, wrap: bool, language:Optional[str] = None):
    if self.attributes['arguments'] is None:
        self.attributes['arguments'] = {}

    linenos = False
    if ('numbers' in self.attributes['arguments']
        or 'numbers' in self.ownerDocument.userdata['listings']):
        linenos = 'inline'

    # If this listing includes a label, inform plasTeX.
    if 'label' in list(self.attributes['arguments'].keys()):
        if hasattr(self.attributes['arguments']['label'], 'textContent'):
            self.ownerDocument.context.label(
                self.attributes['arguments']['label'].textContent)
        else:
            self.ownerDocument.context.label(
                self.attributes['arguments']['label'])

    # Check the textual LaTeX arguments and convert them to Python
    # attributes.
    if 'firstline' in list(self.attributes['arguments'].keys()):
        first_line_number = int(self.attributes['arguments']['firstline'])
    else:
        first_line_number = 0

    if 'lastline' in list(self.attributes['arguments'].keys()):
        last_line_number = int(self.attributes['arguments']['lastline'])
    else:
        last_line_number = sys.maxsize

    # Read the file, all the while respecting the "firstline" and
    # "lastline" arguments given in the document.
    self.plain_listing = ''
    for current_line_number, line in enumerate(file.split('\n')):
        current_line_number += 1
        if (current_line_number >= first_line_number) and \
           (current_line_number <= last_line_number):
            # Remove single-line "listings" comments. Only
            # comments started by "/*@" and ended by "@*/" are
            # supported.
            line = re.sub(r'/\*@[^@]*@\*/', '', line)

            # Add the just-read line to the listing.
            if hasattr(file, 'read'):
                self.plain_listing += line
            else:
                self.plain_listing += '\n' + line


    # Create a syntax highlighted XHTML version of the file using Pygments
    if pygments is not None:
        ctx = self.ownerDocument.context
        try:
            lexer = lexers.get_lexer_by_name(language or ctx.current_language.lower())
        except Exception as msg:
            lexer = lexers.TextLexer()
        self.html_listing = pygments.highlight(self.plain_listing, lexer,
                HtmlFormatter(linenos=linenos, nowrap=not wrap))
