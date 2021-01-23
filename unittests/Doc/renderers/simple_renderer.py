from pathlib import Path
import string
from plasTeX.TeX import TeX
from plasTeX.Renderers import Renderer as _Renderer

class Renderer(_Renderer):

    def default(self, node):
        """ Rendering method for all non-text nodes """
        s = []

        # Handle characters like \&, \$, \%, etc.
        if len(node.nodeName) == 1 and node.nodeName not in string.ascii_letters:
            return self.textDefault(node.nodeName)

        # Start tag
        s.append('<%s>' % node.nodeName)

        # See if we have any attributes to render
        if node.hasAttributes():
            s.append('<attributes>')
            for key, value in node.attributes.items():
                # If the key is 'self', don't render it
                # these nodes are the same as the child nodes
                if key == 'self':
                    continue
                s.append('<%s>%s</%s>' % (key, str(value), key))
            s.append('</attributes>')

        # Invoke rendering on child nodes
        s.append(str(node))

        # End tag
        s.append('</%s>' % node.nodeName)

        return u'\n'.join(s)

    def textDefault(self, node):
        """ Rendering method for all text nodes """
        return node.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# Instantiate a TeX processor and parse the input text
tex = TeX()
tex.ownerDocument.config['files']['split-level'] = -100
tex.ownerDocument.config['files']['filename'] = 'test.xml'
tex.input(r'''
\documentclass{book}
\begin{document}

Previous paragraph.

\section{My Section}

\begin{center}
Centered text with <, >, and \& charaters.
\end{center}

Next paragraph.

\end{document}
''')
document = tex.parse()

def test_simple_renderer_example(tmpdir):
    # Render the document
    renderer = Renderer()
    with tmpdir.as_cwd():
        renderer.render(document)
    out_path = Path(tmpdir)/'test.xml'
    assert out_path.exists()
    assert out_path.read_text() == r"""<document>
<par>
Previous paragraph. 
</par><section>
<attributes>
<*modifier*>None</*modifier*>
<toc>None</toc>
<title>My Section</title>
</attributes>
<par>
<center>
 Centered text with &lt;, &gt;, and &amp; charaters. 
</center>
</par><par>
Next paragraph. 
</par>
</section>
</document>"""


def handle_section(node):
    return '\n\n<%s title="%s">\n%s\n</%s>\n' % \
            (node.nodeName, str(node.attributes['title']),
             str(node), node.nodeName)


def test_extended_simple_renderer_example(tmpdir):
    # Render the document
    renderer = Renderer()
    renderer['section'] = handle_section
    renderer['subsection'] = handle_section
    renderer['subsubsection'] = handle_section
    renderer['paragraph'] = handle_section
    renderer['subparagraph'] = handle_section
    with tmpdir.as_cwd():
        renderer.render(document)
    out_path = Path(tmpdir)/'test.xml'
    assert out_path.exists()
    assert out_path.read_text() == r"""<document>
<par>
Previous paragraph. 
</par>

<section title="My Section">
<par>
<center>
 Centered text with &lt;, &gt;, and &amp; charaters. 
</center>
</par><par>
Next paragraph. 
</par>
</section>

</document>"""

def handle_tikzcd(node):
    return '<div><img src="%s"/></div>' % node.image.url

def test_simple_renderer_tikzcd_image(tmpdir):
    # Instantiate a TeX processor and parse the input text
    tex = TeX()
    tex.ownerDocument.config['files']['split-level'] = -100
    tex.ownerDocument.config['files']['filename'] = 'test.xml'

    tex.input(r'''
    \documentclass{article}
    \usepackage{tikz-cd}

    \begin{document}

    Previous paragraph.

    \begin{tikzcd}
    A \dar \rar & B \dar \\
    C \rar & D
    \end{tikzcd}

    Next paragraph.
    \end{document}
    ''')
    document = tex.parse()

    # Instantiate the renderer
    renderer = Renderer()

    # Insert the rendering method into all of the environments that might need it
    renderer['tikzcd'] = handle_tikzcd

    # Render the document
    with tmpdir.as_cwd():
        renderer.render(document)
    out_path = Path(tmpdir)/'test.xml'
    assert (Path(tmpdir)/'images'/'img-0001.png').exists()
    assert out_path.exists()
    assert out_path.read_text() == r"""<document>
<par>
Previous paragraph. 
</par><par>
<div><img src="images/img-0001.png"/></div>
</par><par>
Next paragraph. 
</par>
</document>"""
