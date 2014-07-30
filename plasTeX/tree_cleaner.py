"""This module contains code to perform transformations on the parse
tree before rendering.

Author: Allen B. Downey
Copyright 2012 Allen B. Downey

Same license as the rest of plasTeX.
"""

import codecs
import os
import subprocess

from lxml import etree

from plasTeX.Base.LaTeX.Math import MathSymbol


class TreeCleaner(object):
    def __init__(self, tex, document):
        self.tex = tex
        self.document = document

        with Tralics() as self.tralics:
            self.clean()

    def clean(self):
        """Walk the node tree fixing problems.

        tex:
        document: TeXDocument
        """
        fp = codecs.open('plastex.before', 'w', encoding='utf-8')
        fp.write(self.document.toXML())
        fp.close()

        print '-----------------------'
        self.walk(self.document, self.test_node)
        print '-----------------------'

        fp = codecs.open('plastex.after', 'w', encoding='utf-8')
        fp.write(self.document.toXML())
        fp.close()

    def walk(self, node, func):
        """Walks a node tree and invokes a function on each node.

        node: Node
        func: function object
        """
        for child in node.childNodes:
            self.walk(child, func)
        func(node)

    def test_node(self, node):
        """Checks for problems and fixes them.

        Checks for things that should not be embedded in par.

        node: Node
        """
        self.test_par(node)
        self.test_quote(node)
        self.test_figure(node)
        self.test_math(node)

    def test_math(self, node):
        """Checks for math tags we can convert to mathphrases.

        node: Node
        """
        if node.nodeName not in ['math', 'displaymath']:
            return

        # translate complicated math into MathML
        if self.is_simple_math(node):
            new_node = self.make_mathit(node)
        else:
            new_node = self.make_mathml(node)

        self.replace(node, [new_node])

    def make_mathit(self, node):
        """Translates simple math into mathit."""
        children = node.childNodes

        phrase = self.document.createElement('mathit')
        phrase.extend(children)

        return phrase

    def make_mathphrase(self, node):
        """Translates simple math into mathphrase."""
        print 'before'
        self.print_tree(node, '')

        children = node.childNodes

        # math becomes mathphrase, which is rendered as inlinequation
        # displaymath becomes displaymathphrase, rendered as equation
        phrase = self.document.createElement(node.nodeName + 'phrase')
        phrase.extend(children)

        print 'after'
        self.print_tree(phrase, '')

        return phrase

    def make_mathml(self, node):
        """Converts a math expression to MathML.

        node: tree of DOM.Element

        Returns: tree of DOM.Element
        """
        # use tralics to generate MathML
        latex = node.source
        print 'latex', latex
        mathml = self.tralics.translate(latex)
        print 'mathml', mathml

        # parse the MathML
        root = etree.fromstring(mathml)
        print 'dom', root

        # strip the formula tag
        assert root.tag == 'formula'
        root = root[0]

        # convert from etree.Element to DOM.Node 
        math = self.convert_elements(root)
        print math.toXML()

        # wrap the whole thing in the right kind of tag
        tag_dict = dict(math='inlineequation',
                        displaymath='informalequation')

        tag = tag_dict[node.nodeName]
        result = self.document.createElement(tag)
        result.append(math)

        return result

    def convert_elements(self, root):
        """Converts a tree of etree.Elements to a tree of DOM.Nodes.

        root: etree.Element
        
        Returns: DOM.Node
        """
        print root, root.text
        tag = root.tag.replace('{http://www.w3.org/1998/Math/MathML}', 'mml')
        node = self.document.createElement(tag)

        if root.text is not None:
            node.append(self.document.createTextNode(root.text))

        for child in root:
            node.append(self.convert_elements(child))

        print node, node[0]
        return node

    def is_simple_math(self, node):
        """Decides if a math expression is simple enough to make into
        a mathphrase, rather than translating into MathML.

        node: DOM.Node

        Returns: boolean
        """
        #TODO: if there's a superscript and subscript on the same
        # character, it's not simple

        # TODO: expand this list of bad commands, or invert the logic
        # and enumerate acceptable commands

        # if it's a bad command, it's not simple
        if node.nodeName in ['sum', 'int']:
            print node.nodeName
            return False

        # if it's text, it's simple
        if node.nodeName == '#text':
            print '#text', node
            return True

        # if it's a math symbol with known Unicode, it's simple;
        # if we don't know the Unicode, it's not
        if isinstance(node, MathSymbol):
            print 'MathSymbol', node.unicode
            if node.unicode is not None:
                return True
            else:
                return False

        # if any of the children are not simple, it's not simple
        for child in node.childNodes:
            if not self.is_simple_math(child):
                return False

        # if we get this far, it's simple
        return True
                
    def test_figure(self, node):
        """Checks for bad paragraphs inside figures.

        node: Node
        """
        if node.nodeName != 'figure':
            return

        # if the first node is a par, unpack it
        child = node.firstChild
        if child.nodeName != 'par':
            return

        self.unpack(child)

    def test_quote(self, node):
        """Checks for quote text not wrapped in a paragraph.

        node: Node
        """
        if node.nodeName not in ['quote', 'quotation', 'exercise']:
            return

        children = node.childNodes
        child = children[0]
        if child.nodeName == 'par':
            return

        # if the quote contains bare text, wrap it in a par
        par = self.document.createElement('par')
        par.extend(children)
        while node.childNodes:
            node.pop(-1)
        node.insert(0, par)

    def print_node(self, node):
        print node.nodeName
        for child in node.childNodes:
            print '    ', child.nodeName

    def print_tree(self, node, prefix):
        if node.nodeName == '#text':
            print prefix + node
        else:
            print prefix + node.nodeName

        for child in node.childNodes:
            self.print_tree(child, prefix + '   ')

    def test_par(self, node):
        """Checks for things that should not be embedded in par.

        node: Node
        """
        if node.nodeName != 'par':
            return

        children = node.childNodes
        if len(children) == 0:
            return

        first = children[0]
        if first.nodeName == '#text':
            return

        # list of nodeNames that should not be embedded in par
        bad_names = set(['itemize', 'description', 'enumerate', 'quote',
                         'verbatim', 'par', 'figure', 'centerline', 'label'])

        if first.nodeName not in bad_names:
            # print 'Allowing embedded', first.nodeName
            return

        self.replace(node, children)

    def unpack(self, node):
        """Replaces a node with its children.

        node: Node
        """
        self.replace(node, node.childNodes)

    def replace(self, child, replacements):
        """Replaces a node with a list of nodes.

        Modifies the parent of child.

        child: Node
        replacement: list of Nodes
        """
        parent = child.parentNode
        for i, node in enumerate(parent):
            if node == child:
                parent.pop(i)
                for j, replacement in enumerate(replacements):
                    parent.insert(i+j, replacement)
                return
        raise ValueError('Child not found.')


class Tralics(object):
    """Wrapper around a Tralics subprocess."""

    def __init__(self, executable='/usr/local/bin/tralics'):
        """Create a subprocess to communicate with Tralics.

        executable: string full path to tralics executable
        """
        self.executable = executable
        if not os.path.exists(executable):
            raise ValueError('Unable to locate the executable ' +
                             self.executable)

    def __enter__(self):
        """Creates the subprocess (for use with the with statement)."""
        cmd = [self.executable, 
               '-interactivemath',
               '-noconfig',
               '-entnames=no']
        self.process = subprocess.Popen(cmd, 
                                        shell=False, 
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        )
        for i in range(4):
            output = self.process.stdout.readline()
            print 'enter', output

        err = self.process.stdout.readline()
        print 'enter', err
        return self

    def translate(self, latex):
        """Translates a LaTeX math expression into MathML.

        If the expression is display math (starts with '\['), we
        have to work around some strange Tralics behavior by sending
        and extra expression and reading an extra line.

        latex: string

        Returns: string XML
        """
        latex = latex.strip()
        self.process.stdin.write(latex + '\n')
            
        output = self.process.stdout.readline()
        return output.strip()

    def __exit__(self, kind, value, traceback):
        """Terminates the subprocess (for use with the with statement)."""
        print 'Terminating tralics...'
        self.process.terminate()
        #output = self.process.stdout.readline()
        #print 'close', output
        #self.process.stdin.write('y')
        self.process.wait()
        print 'Done.'


def main():
    tralics = Tralics()

    print tralics.translate('$\int_0^{\infty} x^{-2} dx$')
    print tralics.translate('\[ x + 1 \]')
    print tralics.translate('$\int_0^{\infty} x^{-2} dx$')
    tralics.close()


if __name__ == '__main__':
    main()
