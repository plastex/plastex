#!/usr/bin/env python

"""
ZPT - Zope Page Template Renderer

This module contains a plasTeX renderer that uses Zope Page Templates
(actually simpleTAL) as the templating engine.

"""

import sys, os, re, codecs, plasTeX
from plasTeX.Renderers import Renderer as BaseRenderer
from plasTeX.simpletal import simpleTAL, simpleTALES
from plasTeX.simpletal.simpleTALES import Context as TALContext
from plasTeX.simpletal.simpleTALUtils import FastStringOutput as StringIO

log = plasTeX.Logging.getLogger()

def _render(self, obj, outputFile=None, outputEncoding=None, interpreter=None):
    """ 
    New rendering method for HTML templates 

    This function is used as the __call__ method on page templates to
    make them callable.  They need to be callable in order to work
    with Renderer.  This function was written to be argument-compatible
    with the expand() method, but some arguments are ignored.

    Required Arguments:
    obj -- the object to be rendered
   
    Keyword Arguments:
    outputFile -- the file object to write the resultant content to. (ignored)
    outputEncoding -- the encoding to use in the output file (ignored)
    interpreter -- passed as the interpreter to the page template's 
        expand method

    Returns:
    unicode object containing rendered node

    """
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', obj.ownerDocument.userdata['config'])
    context.addGlobal('template', self)
    context.addGlobal('templates', obj.renderer)
    output = StringIO()
    self.expand(context, output, 'utf-8', interpreter)
    return unicode(output.getvalue(), 'utf-8')

simpleTAL.HTMLTemplate.__call__ = _render

def _render(self, obj, outputFile=None, outputEncoding=None, docType=None, suppressXMLDeclaration=1, interpreter=None):
    """ 
    New rendering method for XML templates

    This function is used as the __call__ method on page templates to
    make them callable.  They need to be callable in order to work
    with Renderer.  This function was written to be argument-compatible
    with the expand() method, but some arguments are ignored.

    Required Arguments:
    obj -- the object to be rendered
   
    Keyword Arguments:
    outputFile -- the file object to write the resultant content to. (ignored)
    outputEncoding -- the encoding to use in the output file (ignored)
    docType -- the document type for this XML document
    suppressXMLDeclaration -- if true, the XML declaration is not included
        in the output
    interpreter -- passed as the interpreter to the page template's 
        expand method

    Returns:
    unicode object containing rendered node

    """
    context = TALContext(allowPythonPath=1)
    context.addGlobal('here', obj)
    context.addGlobal('self', obj)
    context.addGlobal('config', obj.ownerDocument.userdata['config'])
    context.addGlobal('template', self)
    context.addGlobal('templates', obj.renderer)
    output = StringIO()
    self.expand(context, output, 'utf-8', docType, suppressXMLDeclaration, interpreter)
    return unicode(output.getvalue(), 'utf-8')

simpleTAL.XMLTemplate.__call__ = _render

# shortcuts
htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate

class ZPT(BaseRenderer):
    """ Renderer for XHTML documents """

    outputtype = unicode

    def textdefault(self, node):
        """ 
        Default renderer for text nodes 

        This method makes sure that special characters are converted to
        entities.

        Arguments:
        node -- the Text node to process

        """
        node = node.replace('&', '&amp;')
        node = node.replace('<', '&lt;')
        node = node.replace('>', '&gt;')
        return node

    def initialize(self):
        """ Load and compile page templates """
        # Load templates from renderer directory and parent 
        # renderer directories
        sup = list(type(self).__mro__)
        sup.reverse()
        for cls in sup:
            if cls is BaseRenderer or cls is object or cls is dict:
                continue
            cwd = os.path.dirname(sys.modules[cls.__module__].__file__)
            log.info('Importing templates from %s' % cwd)
            self.importDirectory(cwd)

            # Load templates configured by the environment variable
            templates = os.environ.get('%sTEMPLATES' % cls.__name__,'')
            for path in [x.strip() for x in templates.split(':') if x.strip()]:
                log.info('Importing templates from %s' % path)
                self.importDirectory(path)

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
        # Create a list for resolving aliases
        self.aliases = []

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

        if self.aliases:
           log.warning('The following aliases were unresolved: %s' 
                       % ', '.join(self.aliases)) 

    def setTemplate(self, template, options):
        """ 
        Compile template and set it in the renderer 

        Required Arguments:
        template -- the content of the template to be compiled
        options -- dictionary containing the name (or names) and type 
            of the template

        """

        # Get name
        try:
            names = options['name'].split()
            if not names:
                names = [' ']
        except KeyError:
            raise ValueError, 'No name given for template'

        # If an alias was specified, link the names to the 
        # already specified template.
        if 'alias' in options:
            self.aliases.append(options['alias'].strip())
            for i in range(len(self.aliases)-1, -1, -1):
                if self.aliases[i] in self:
                    for name in names:
                        self[name] = self[self.aliases[i]]
                    self.aliases.pop(i)

            if ''.join(template).strip():
                log.warning('Both an alias and a template were specified for: %s' % ', '.join(names))

            return

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

# Set Renderer variable so that plastex will know how to load it
Renderer = ZPT

