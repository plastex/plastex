#!/usr/bin/env python

import sys, os, re, codecs
from plasTeX.Config import config
from plasTeX.Renderer import Renderer
from plasTeX.TALUtils import htmltemplate, xmltemplate

encoding = config['encoding']['output']

# Regular expressions for multi-zpt files
templatere = re.compile(r'(<zpt:page-template\s+[^>]+>.*?</zpt:page-template>)', re.S)
attrsre = re.compile(r'<zpt:page-template\s+([^>]+)?\s*>')
parseattrsre = re.compile(r'\s*(\w+)\s*=\s*["\']([^"\']+)?["\']')
contentre = re.compile(r'<zpt:page-template\s+[^>]+>(.*?)</zpt:page-template>', re.S)

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
                file = os.path.join(templatedir, file)
                ext = os.path.splitext(file)[-1]

                # Multi-zpt files
                if ext.lower() == '.zpts':
                    content = codecs.open(file,'r').read().strip()
                    templates = templatere.split(content)
                    templates.pop()
                    while templates:
                        templates.pop(0)
                        template = templates.pop(0)
 
                        # Get macro attributes
                        attrs = attrsre.search(template).group(1) 
                        attrs = dict(parseattrsre.findall(attrs))

                        # Get content of macro
                        content = contentre.search(template).group(1) 

                        # Compile the template
                        if attrs.get('type','').lower() == 'xml':
                            try: template = xmltemplate(content) 
                            except Exception, msg: 
                                print 'Error in compiling %s (%s)' % (file, msg)
                        else:
                            try: template = htmltemplate(content) 
                            except Exception, msg: 
                                print 'Error in compiling %s (%s)' % (file, msg)

                        # Get all names in the 'name' attribute
                        names = [x.strip() for x in attrs['name'].split() 
                                           if x.strip()]
                        for name in names:
                            self[name] = template

            # Now compile macros in individual files.  These have
            # a higher precedence than macros found in multi-zpt files.
            for file in files:
                file = os.path.join(templatedir, file)
                ext = os.path.splitext(file)[-1]

                # Single zpt files
                if ext.lower() in ['.zpt','.html','.htm']:
                    content = codecs.open(file,'r').read().strip()
                    key = os.path.splitext(os.path.basename(file))[0]
                    try: self[key] = htmltemplate(content) 
                    except Exception, msg: 
                        print 'Error in compiling %s (%s)' % (file, msg)
                        

                # XML formatted zpt files
                elif ext.lower() == '.xml':
                    content = codecs.open(file,'r').read().strip()
                    key = os.path.splitext(os.path.basename(file))[0]
                    try: self[key] = xmltemplate(content) 
                    except Exception, msg: 
                        print 'Error in compiling %s (%s)' % (file, msg)

xhtml = XHTML()

templates = os.environ.get('XHTMLTEMPLATES','')
for path in [x.strip() for x in templates.split(':') if x.strip()]:
    xhtml.importDirectory(path)

if __name__ == '__main__':
    print XHTML()
