#!/usr/bin/env python

import sys, os, re, codecs
from plasTeX.Config import config
from plasTeX.Renderer import Renderer
from plasTeX.TALUtils import htmltemplate, xmltemplate

encoding = config['encoding']['output']

class htmlunicode(unicode):
    """ Helper for strings output from renderer """

    def plaintext(self):
        """ Strip markup from string """
        return type(self)(re.sub(r'</?\w+[^>]*>', r'', self))


class XHTML(Renderer):

    outputtype = htmlunicode

    entitysubs = [ 
        # Pretty quotation marks
        ('``', '&#8220;'),
        ("''", '&#8221;'),
        ('`',  '&#8216;'),
        ("'",  '&#8217;'),
    ]

    def __init__(self):
        Renderer.__init__(self)
        self.importDirectory(os.path.dirname(__file__))

    def default(self, s):
        """ Default renderer """
        s = unicode(s)
        for before, after in type(self).entitysubs:
            s = s.replace(before, after)
        return unicode(s)

    def cleanup(self):
        """ Cleanup method called at the end of rendering """
        for file in self.files:
            s = codecs.open(file, 'r', encoding).read()

            # Clean up empty paragraphs and table cells
            s = re.compile(r'(<p\b[^>]*>)\s*(</p>)', re.I).sub(r'', s)
            s = re.compile(r'(<td\b[^>]*>)\s*(</td>)', re.I).sub(r'\1&nbsp;\2', s)
            
            # Add width, height, and depth to images
            s = re.compile(r'<img\b[^>]+>', re.I).sub(self.setImageData, s) 

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
        tag = tag.replace('#width', str(img.width))
        tag = tag.replace('#height', str(img.height))
        tag = tag.replace('#depth', ('voffset%s' % img.depth).replace('-','_'))

        return tag

    def importDirectory(self, templatedir):
        """ Compile all ZPT files in the given directory """
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
                if ext.lower() in ['.xml']:
                    options['type'] = 'xml'
                elif ext.lower() in ['.zpt','.html','.htm']:
                    options['type'] = 'html'
                else:
                    continue

                self.parseTemplates(file, options)                

    def setTemplate(self, template, options):
        """ Compile template and set it in the renderer """
        names = options.get('name','').split()

        # No name found
        if not names:
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
                name, value = line.split(' ', 1)
                value = value.rstrip()
                while value.endswith('\\'):
                    value = value[:-1] + ' '
                    for line in file:
                        value += line.rstrip()
                        break

                options[name[:-1]] = re.sub(r'\s+', r' ', value.strip())
                continue
            
            template.append(line)

        # Purge any awaiting templates
        if template:
            try:
                self.setTemplate(''.join(template), options)
            except ValueError, msg:
                print 'ERROR: %s at line %s in file %s' % (msg, i, filename)

xhtml = XHTML()

templates = os.environ.get('XHTMLTEMPLATES','')
for path in [x.strip() for x in templates.split(':') if x.strip()]:
    xhtml.importDirectory(path)

if __name__ == '__main__':
    print XHTML()
