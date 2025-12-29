"""
C.6.2 List-Making Environments
C.6.3 The list and trivlist Enviroments

"""

from plasTeX import Environment, Command, DimenCommand
from plasTeX.encoding import numToRoman, numToAlpha

class enuminame(Command): str = ''
class enumiiname(Command): str = ''
class enumiiiname(Command): str = ''
class enumivname(Command): str = ''

class List(Environment):
    """ Base class for all list-based environments """
    depth = 0
    counters = ['enumi','enumii','enumiii','enumiv']
    blockType = True
    allowedChildren = None # A list of names of nodes that can be direct children of this node.

    class item(Command):
        args = '[ term ]'
        counter = 'enumi'
        position = 0
        forcePars = True

        def invoke(self, tex):
            """ Set up counter for this list depth """
            try:
                self.counter = List.counters[List.depth-1]
                self.position = self.ownerDocument.context.counters[self.counter].value + 1
            except (KeyError, IndexError):
                pass
            return Command.invoke(self, tex)

        def digest(self, tokens):
            """
            Items should absorb all of the content within that 
            item, not just the `[...]' argument.  This is 
            more useful for the resulting document object.

            """
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                tokens.push(tok)
                break
            self.digestUntil(tokens, List.item)
            if self.forcePars:
                self.paragraphs()

    def invoke(self, tex):
        """ Set list nesting depth """
        if self.macroMode != Environment.MODE_END:
            List.depth += 1
        else:
            List.depth -= 1
        try:
            for i in range(List.depth, len(List.counters)):
                self.ownerDocument.context.counters[List.counters[i]].setcounter(0)
        except (IndexError, KeyError):
            pass
        return Environment.invoke(self, tex)

    def digest(self, tokens):
        if self.macroMode != Environment.MODE_END:
            # Drop any whitespace before the first item
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                elif tok.nodeName == 'setcounter':
                    tok.digest([])
                    continue
                elif self.allowedChildren is not None and tok.nodeName not in self.allowedChildren:
                    continue
                tokens.push(tok)
                break
        Environment.digest(self, tokens) 

        self.has_custom_terms = any(tok.nodeName == 'item' and tok.attributes.get('term') is not None for tok in self.childNodes) or getattr(self, 'listType', None)

#
# Counters -- enumi, enumii, enumiii, enumiv
#            

# C.6.2
    
class itemize(List): 
    pass

class labelitemi(Command):
    pass
class labelitemii(Command):
    pass
class labelitemiii(Command):
    pass
class labelitemiv(Command):
    pass

def term_label_formatter(label_format):
    """ Format the label for a list item.
        Each of the special characters is replaced by the corresponding encoding of the item's position in the list.
        All other characters are passed through unmodified.
    """
    formats = {
        'I': lambda i: numToRoman(i).upper(),
        'i': lambda i: numToRoman(i).lower(),
        '1': lambda i: str(i),
        'a': lambda i: numToAlpha(i).lower(),
        'A': lambda i: numToAlpha(i).upper(),
    }

    def format_term(position):
        return ''.join(formats.get(c, lambda _: c)(position) for c in label_format)

    return format_term

class enumerate_(List): 
    macroName = 'enumerate'
    args = '[ type:str ]'  # Actually defined in the enumerate package, but it doesn't hurt
    allowedChildren = ('item',)
    listType = None

    label_formats = {
        2: '(a)',
        3: 'i.',
        4: 'A.',
    }

    def term(self, position):
        if self.listType:
            label_format = self.listType
        else:
            label_format = self.label_formats.get(self.listDepth, '1.')
        formatter = term_label_formatter(label_format)
        return formatter(position)

    def invoke(self, tex):
        super().invoke(tex)

        self.listType = self.attributes.get('type')

        self.listDepth = List.depth

    class item(List.item):
        @property  # type: ignore # mypy#4125
        def ref(self):
            doc = self.ownerDocument
            frag = doc.createDocumentFragment()
            terms = []

            item = self
            node = self.parentNode
            while item is not None:
                while node is not None and not (isinstance(node, enumerate_)):
                    item = node
                    node = node.parentNode
                if not (issubclass(type(item), List.item)):
                    break
                terms.append(node.term(int(str(item._ref))).rstrip('.'))
                item = node
                node = node.parentNode

            for t in reversed(terms):
                frag.append(t)
            return frag

        @ref.setter
        def ref(self, value):
            self._ref = value

class description(List): 
    pass

# C.6.3

class trivlist(List): 
    pass

class ConfigurableList(List):
    macroName = 'list'
    args = 'defaultlabel decls:nox'

class topsep(DimenCommand):
    value = DimenCommand.new(0)

class partopsep(DimenCommand):
    value = DimenCommand.new(0)

class itemsep(DimenCommand):
    value = DimenCommand.new(0)

class parsep(DimenCommand):
    value = DimenCommand.new(0)

class leftmargin(DimenCommand):
    value = DimenCommand.new(0)

class rightmargin(DimenCommand):
    value = DimenCommand.new(0)

class listparindent(DimenCommand):
    value = DimenCommand.new(0)

class itemindent(DimenCommand):
    value = DimenCommand.new(0)

class labelsep(DimenCommand):
    value = DimenCommand.new(0)

class labelwidth(DimenCommand):
    value = DimenCommand.new(0)

class makelabel(Command):
    args = 'label'

class usecounter(Command):
    args = 'name:str'
