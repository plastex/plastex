#!/usr/bin/env python

"""
ZPT - Zope Page Template Renderer

This module contains a plasTeX renderer that uses Zope Page Templates
(actually simpleTAL) as the templating engine.

"""

import sys, os, re, codecs, plasTeX, shutil
from plasTeX.Renderers import Renderer as BaseRenderer
from simpletal import simpleTAL, simpleTALES
from simpletal.simpleTALES import Context as TALContext
from simpletal.simpleTALUtils import FastStringOutput as StringIO

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
    context.addGlobal('container', obj.parentNode)
    context.addGlobal('config', obj.ownerDocument.config)
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
    context.addGlobal('container', obj.parentNode)
    context.addGlobal('config', obj.ownerDocument.config)
    context.addGlobal('template', self)
    context.addGlobal('templates', obj.renderer)
    output = StringIO()
    self.expand(context, output, 'utf-8', docType, suppressXMLDeclaration, interpreter)
    return unicode(output.getvalue(), 'utf-8')

simpleTAL.XMLTemplate.__call__ = _render

# shortcuts
htmltemplate = simpleTAL.compileHTMLTemplate
xmltemplate = simpleTAL.compileXMLTemplate


def copytree(src, dest, symlink=None):
    """ 
    This is the same as shutil.copytree, but doesn't error out if the 
    directories already exist.

    """
    for root, dirs, files in os.walk(src, True):
        for d in dirs:
            srcpath = os.path.join(root, d)
            destpath = os.path.join(dest, root, d)
            if symlink and os.path.islink(srcpath):
                os.symlink(os.readlink(srcpath), destpath)
            elif not os.path.isdir(destpath):
                os.makedirs(destpath)
                shutil.copymode(srcpath, destpath)
                shutil.copystat(srcpath, destpath)
        for f in files:
            srcpath = os.path.join(root, f)
            destpath = os.path.join(dest, root, f)
            if symlink and os.path.islink(srcpath):
                os.symlink(os.readlink(srcpath), destpath)
            else:
                shutil.copy2(srcpath, destpath)


class ZPT(BaseRenderer):
    """ Renderer for XHTML documents """

    outputType = unicode
    fileExtension = '.xml'

    def textDefault(self, node):
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

    def render(self, document):
        """ Load and compile page templates """
        themename = document.config['general']['theme']

        # Load templates from renderer directory and parent 
        # renderer directories
        sup = list(type(self).__mro__)
        sup.reverse()
        themes = []
        for cls in sup:
            if cls is BaseRenderer or cls is object or cls is dict:
                continue
            cwd = os.path.dirname(sys.modules[cls.__module__].__file__)
            log.info('Importing templates from %s' % cwd)
            self.importDirectory(cwd)

            # Store theme location
            themes.append(os.path.join(cwd, 'Themes', themename))

            # Load templates configured by the environment variable
            templates = os.environ.get('%sTEMPLATES' % cls.__name__,'')
            for path in [x.strip() for x in templates.split(os.pathsep) if x.strip()]:
                log.info('Importing templates from %s' % path)
                self.importDirectory(path)
                themes.append(os.path.join(path, 'Themes', themename))

        # Load only one theme
        for theme in reversed(themes):
            if os.path.isdir(theme):
                log.info('Importing templates from %s' % theme)
                self.importDirectory(theme)

                if document.config['general']['copy-theme-extras']:
                    # Copy all theme extras
                    cwd = os.getcwd()
                    os.chdir(theme)
                    for item in os.listdir('.'):
                        if os.path.isdir(item):
                            if not os.path.isdir(os.path.join(cwd,item)):
                                os.makedirs(os.path.join(cwd,item))
                            copytree(item, cwd, True)
                        elif os.path.splitext(item)[-1].lower() not in \
                                 ['.html','.htm','.zpt','.zpts',
                                  '.xml','.xhtml','.xhtm']:
                            shutil.copy(item, os.path.join(cwd,item))
                    os.chdir(cwd)

                break

        BaseRenderer.render(self, document)

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
        self.aliases = {}

        if templatedir and os.path.isdir(templatedir):
            files = os.listdir(templatedir)

            # Compile multi-zpt files first
            for f in files:
                ext = os.path.splitext(f)[-1]
                f = os.path.join(templatedir, f)

                if not os.path.isfile(f):
                    continue

                # Multi-zpt files
                if ext.lower() == '.zpts':
                    self.parseTemplates(f)

            # Now compile macros in individual files.  These have
            # a higher precedence than macros found in multi-zpt files.
            for f in files:
                basename, ext = os.path.splitext(f)
                f = os.path.join(templatedir, f)

                if not os.path.isfile(f):
                    continue

                options = {'name':basename}
                if ext.lower() in ['.xml','.xhtml','.xhtm']:
                    options['type'] = 'xml'
                elif ext.lower() in ['.zpt','.html','.htm']:
                    options['type'] = 'html'
                else:
                    continue

                self.parseTemplates(f, options)                

        if self.aliases:
           log.warning('The following aliases were unresolved: %s' 
                       % ', '.join(self.aliases.keys())) 

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
            alias = options['alias'].strip()
            for name in names:
                self.aliases[name] = alias
            if ''.join(template).strip():
                log.warning('Both an alias and a template were specified for: %s' % ', '.join(names))

        # Resolve remaining aliases
        for key, value in self.aliases.items():
            if value in self:
                self[key] = self[value]
            self.aliases.pop(key)

        if 'alias' in options:
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
        if not options:
            f = open(filename, 'r')
            for i, line in enumerate(f):
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
                        for line in f:
                            value += line.rstrip()
                            break
    
                    options[name] = re.sub(r'\s+', r' ', value.strip())
                    continue
                
                template.append(line)

        else:
            template = open(filename, 'r').readlines()
    
        # Purge any awaiting templates
        if template:
            try:
                self.setTemplate(''.join(template), options)
            except ValueError, msg:
                print 'ERROR: %s in template %s in file %s' % (msg, ''.join(template), filename)

        elif name and not(template):
            self.setTemplate('', options)

    def processFileContent(self, document, s):
        # Add width, height, and depth to images
        s = re.sub(r'&amp;(\S+)-(width|height|depth);(?:&amp;([a-z]+);)?', 
                   self.setImageData, s) 

        # Convert characters >127 to entities
        if document.config['files']['escape-high-chars']:
            s = list(s)
            for i, item in enumerate(s):
                if ord(item) > 127:
                    s[i] = '&#%.3d;' % ord(item)
            s = u''.join(s)

        return BaseRenderer.processFileContent(self, document, s)
             
    def setImageData(self, m):
        """
        Substitute in width, height, and depth parameters in image tags

        The width, height, and depth parameters aren't known until after
        all of the output has been generated.  We have to post-process
        the files to insert this information.  This method replaces
        the &filename-width;, &filename-height;, and &filename-depth; 
        placeholders with their appropriate values.

        Required Arguments:
        m -- regular expression match object that contains the filename
            and the parameter: width, height, or depth.

        Returns:
        replacement for entity

        """
        filename, parameter, units = m.group(1), m.group(2), m.group(3)

        try:
            img = self.imager.images.get(filename, self.vectorImager.images.get(filename, self.imager.staticimages.get(filename)))
            if img is not None and getattr(img, parameter) is not None:
                if units:
                    return getattr(getattr(img, parameter), units)
                return str(getattr(img, parameter))
        except KeyError: pass

        return '&%s-%s;' % (filename, parameter)


# Set Renderer variable so that plastex will know how to load it
Renderer = ZPT

