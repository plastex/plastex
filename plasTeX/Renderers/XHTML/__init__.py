#!/usr/bin/env python

import sys, os, re, codecs, plasTeX
from plasTeX.Renderer import Renderer
from plasTeX.simpletal import simpleTAL, simpleTALES
from plasTeX.simpletal.simpleTALES import Context as TALContext
from plasTeX.simpletal.simpleTALUtils import FastStringOutput as StringIO
from plasTeX.Config import config

log = plasTeX.Logging.getLogger()

def _render(self, obj, outputFile=None, outputEncoding=config['files']['output-encoding'], interpreter=None):
    """ 
    New rendering method for HTML templates 

    This function is used as the __call__ method on page templates to
    make them callable.  They need to be callable in order to work
    with Renderer.

    Required Arguments:
    obj -- the object to be rendered
   
    Keyword Arguments:
    outputFile -- the file object to write the resultant content to.
        By default, this comes from `obj`.
    outputEncoding -- the encoding to use in the output file
    interpreter -- passed as the interpreter to the page template's 
        expand method

    Returns:
    string containing the content not written to an output file

    """
    output = outputFile
    if obj.filename or outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    context.addGlobal('templates', obj.renderer)
    self.expand(context, output, outputEncoding, interpreter)
    if obj.filename:
        obj.renderer.write(obj.filename, output.getvalue())
        return u''
    else:
        return output.getvalue()
simpleTAL.HTMLTemplate.__call__ = _render

def _render(self, obj, outputFile=None, outputEncoding=config['files']['output-encoding'], docType=None, suppressXMLDeclaration=1, interpreter=None):
    """ 
    New rendering method for XML templates

    This function is used as the __call__ method on page templates to
    make them callable.  They need to be callable in order to work
    with Renderer.

    Required Arguments:
    obj -- the object to be rendered
   
    Keyword Arguments:
    outputFile -- the file object to write the resultant content to.
        By default, this comes from `obj`.
    outputEncoding -- the encoding to use in the output file
    docType -- the document type for this XML document
    suppressXMLDeclaration -- if true, the XML declaration is not included
        in the output
    interpreter -- passed as the interpreter to the page template's 
        expand method

    Returns:
    string containing the content not written to an output file

    """
    output = outputFile
    if obj.filename or outputFile is None:
        output = StringIO()
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', config)
    context.addGlobal('template', self)
    context.addGlobal('templates', obj.renderer)
    self.expand(context, output, outputEncoding, docType, suppressXMLDeclaration, interpreter)
    if obj.filename:
        obj.renderer.write(obj.filename, output.getvalue())
        return u''
    else:
        return output.getvalue()
simpleTAL.XMLTemplate.__call__ = _render

# shortcuts
htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate

class XHTML(Renderer):
    """ Renderer for XHTML documents """

    outputtype = unicode

    entitysubs = [ 
#       ('&', '&amp;'),
#       ('<', '&lt;'),
#       ('>', '&gt;'),
        # Pretty quotation marks
        ('``', '&#8220;'),
        ("''", '&#8221;'),
        ('`',  '&#8216;'),
        ("'",  '&#8217;'),
        ('---', '&#8212;'),
        ('--', '&#8211;'),
    ]

    def initialize(self):
        """ Load and compile page templates """
        self.importDirectory(os.path.dirname(__file__))

    def default(self, node):
        """ 
        Default renderer 

        If a node in a document is reached that has no rendering method,
        this method is called in its place.

        Required Arguments:
        node -- node in the document that needs to be rendered

        Returns:
        unicode object containing rendered content

        """
        if isinstance(node, unicode):
#           print type(node.parentNode), node
            for before, after in type(self).entitysubs:
                node = node.replace(before, after)
            return node
        return unicode(node)

    def cleanup(self, document):
        """ 
        Cleanup method called at the end of rendering 

        This method allows you to do arbitrary post-processing after
        all files have been rendered.

        Note: While I greatly dislike post-processing, sometimes it's 
              just easier...

        Required Arguments:
        document -- the document being rendered

        """
        encoding = config['files']['output-encoding']

        for file in self.files:
            try:
                s = codecs.open(str(file), 'r', encoding).read()
            except IOError, msg:
                print os.getcwd()
                log.error(msg)
                continue

            # Clean up empty paragraphs and table cells
            s = re.compile(r'(<p\b[^>]*>)\s*(</p>)', re.I).sub(r'', s)
            s = re.compile(r'(<td\b[^>]*>)\s*(</td>)', re.I).sub(r'\1&nbsp;\2', s)
            
            # Add width, height, and depth to images
            s = re.compile(r'<img\b[^>]+>', re.I).sub(self.setImageData, s) 

            # Force XHTML syntax on empty tags
            s = re.compile(r'(<(?:br|img|link|meta)\b[^>]*)/?(>)', re.I).sub(r'\1 /\2', s)

            open(file, 'w').write(unicode.encode(s, encoding)) 

    def setImageData(self, m):
        """
        Substitute in #width, #height, and #depth parameters in image tags

        The width, height, and depth parameters aren't known until after
        all of the output has been generated.  We have to post-process
        the files to insert this information.  This method replaces
        the #width, #height, and #depth placeholders with their appropriate
        values.

        Note: #depth is actually replaced with a class name called 
              "voffset<depth>" where <depth> is the numberic value.
              In the case of negative values, the '-' is replaced 
              with '_'.

        Required Arguments:
        m -- regular expression match object that contains an img tag

        Returns:
        new image tag with width, height, and depth information

        """
        tag = m.group()

        # If the tag doesn't contain any of these, we're done
        if not re.search(r'#(width|height|depth)', tag):
            return tag

        # Get the filename
        src = re.compile(r'\bsrc\s*=\s*(\'|\")\s*([^\1]+?)\s*\1', 
                         re.I).search(tag)
        if not src:
            return tag

        src = src.group(2)

        # Make sure we have the information we need in the imager
        if not self.imager.images.has_key(src):
            return tag

        img = self.imager.images[src]

        width = img.width
        if width is None:
            width = ''

        height = img.height
        if height is None:
            height = ''

        depth = img.depth
        if depth is None:
            depth = 0

        tag = tag.replace('#width', '%spx' % width)
        tag = tag.replace('#height', '%spx' % height)
        tag = tag.replace('#depth', '%spx' % depth)

        # If we have a large descender (i.e. greater than 8px), 
        # put in this image hack to keep MSIE from truncating the 
        # image if it's within a table cell.
        if height and abs(depth) > 8: 
            tag = '%s<img src="../blank.gif" style="height:%spx" class="ieimgfix">' % (tag, height)

            # We don't want the full height to be used for the line height.
            # After some tuning, a value of (height-8px) was chosen.  That
            # seems to give decent descenders without much overlap.
            tag = '%s<span style="line-height:%spx;visibility:hidden">&#8205;</span>' % (tag, height-8)

        return tag

    def importDirectory(self, templatedir):
        """ 
        Compile all ZPT files in the given directory 

        Templates can exist in two different forms.  First, a template
        can be a file unto itself.  If an XML template is desired, 
        the file should have an extension of .xml, .xhtml, or .xhtm.
        If an HTML template is desired, the files should have an 
        extension of .zpt, .html, or .htm.

        If you have many small templates, or a template that corresponds
        to more than one macro, you can use a multiple ZPT file.  A
        multiple ZPT file contains directives within it to delimit 
        individual page templates as well as specify which macros they
        correspond to and what type of template they are (i.e. XML or
        HTML).

        Required Arguments:
        templatedir -- the directory to search for template files

        """
        if templatedir and os.path.isdir(templatedir):
            files = os.listdir(templatedir)

            # Compile multi-zpt files first
            for file in files:
                ext = os.path.splitext(file)[-1]
                file = os.path.join(templatedir, file)

                if not os.path.isfile(file):
                    continue

                # Multi-zpt files
                if ext.lower() == '.zpts':
                    self.parseTemplates(file)

            # Now compile macros in individual files.  These have
            # a higher precedence than macros found in multi-zpt files.
            for file in files:
                basename, ext = os.path.splitext(file)
                file = os.path.join(templatedir, file)

                if not os.path.isfile(file):
                    continue

                options = {'name':basename}
                if ext.lower() in ['.xml','.xhtml','.xhtm']:
                    options['type'] = 'xml'
                elif ext.lower() in ['.zpt','.html','.htm']:
                    options['type'] = 'html'
                else:
                    continue

                self.parseTemplates(file, options)                

    def setTemplate(self, template, options):
        """ 
        Compile template and set it in the renderer 

        Required Arguments:
        template -- the content of the template to be compiled
        options -- dictionary containing the name (or names )and type 
            of the template

        """

        # Get name
        try:
            names = options['name'].split()
            if not names:
                names = [' ']
        except KeyError:
            raise ValueError, 'No name given for template'

        # Compile template and add it to the renderer
        template = ''.join(template).strip()
        ttype = options.get('type','html').lower()

        try:
            if ttype == 'xml':
                template = xmltemplate(template)
            else:
                template = htmltemplate(template)
        except Exception, msg:
            raise ValueError, 'Could not compile template "%s"' % names[0]

        for name in names:
            self[name] = template

    def parseTemplates(self, filename, options={}):
        """
        Parse templates from the file and set them in the renderer

        Required Arguments:
        filename -- file to parse templates from

        Keyword Arguments:
        options -- dictionary containing initial parameters for templates
            in the file

        """
        template = []
        options = options.copy()
        file = open(filename, 'r')
        for i, line in enumerate(file):
            # Found a meta-data command
            if re.match(r'\w+:', line):

                # Purge any awaiting templates
                if template:
                    try:
                        self.setTemplate(''.join(template), options)
                    except ValueError, msg:
                        print 'ERROR: %s at line %s in file %s' % (msg, i, filename)
                    options.clear()
                    template = []

                # Done purging previous template, start a new one
                name, value = line.split(':', 1)
                name = name.strip()
                value = value.rstrip()
                while value.endswith('\\'):
                    value = value[:-1] + ' '
                    for line in file:
                        value += line.rstrip()
                        break

                options[name] = re.sub(r'\s+', r' ', value.strip())
                continue
            
            template.append(line)

        # Purge any awaiting templates
        if template:
            try:
                self.setTemplate(''.join(template), options)
            except ValueError, msg:
                print 'ERROR: %s at line %s in file %s' % (msg, i, filename)

        elif name and not(template):
            self.setTemplate('', options)

xhtml = XHTML()

templates = os.environ.get('XHTMLTEMPLATES','')
for path in [x.strip() for x in templates.split(':') if x.strip()]:
    xhtml.importDirectory(path)

if __name__ == '__main__':
    print XHTML()
