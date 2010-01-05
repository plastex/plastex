import plasTeX
from plasTeX.TeX import TeX
from plasTeX.Config import config
from plasTeX.ConfigManager import *
from plasTeX.Renderers.XHTML import Renderer as XHTMLRenderer
from plasTeX.Renderers.PageTemplate.simpletal import simpleTAL, simpleTALES
#
import codecs
import datetime
import os
import sgmllib
import zipfile
#
import templates

NCX_DOCTYPE = '''<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
        "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">'''

def split_name(name):
    'utility needed for id attributes to use the stem as the value'
    raw_name = str(name)
    stem = os.path.splitext(raw_name)[0]#raw_name[:raw_name.rfind('.')]            
    return {'stem':os.path.basename(stem), 'fullname':raw_name}

class NameParser(sgmllib.SGMLParser):
    ''' We don't have access to lxml necessarily, so we roll our own parser
        using the SGMLParser as the parent class. This is only used to get the
        image and css filenames inside the xhtml content.
        '''
    def __init__(self, fname, encoding='utf-8'):
        sgmllib.SGMLParser.__init__(self)
        if os.path.isfile(fname):
            f = codecs.open(fname, 'rb', encoding=encoding)
            self.contents = f.read()
            f.close()
        else:
            self.contents = ''

        self.cssnames = list()
        self.imagenames = list()
   
    def start_img(self, attributes):
        tmp = dict(attributes)
        self.imagenames.append(tmp.get('src'))

    def start_link(self, attributes):
        tmp = dict(attributes)
        if tmp.get('rel') == 'stylesheet':
            self.cssnames.append(tmp['href'])

    def parse(self):
        self.feed(self.contents)
        self.close()
       
    def get_cssnames(self):
        return self.cssnames

    def get_imagenames(self):
        return self.imagenames

class Epub_Package(object):
    ''' This is the class that does the work. initialize with a properties 
        dictionary, add some defaults as needed, then:
        (1) get the names of the html files comprising the book (ordered list)
        (2) get the names of the images and css files needed in the book
        '''
    def __init__(self, properties):
        self.name = properties['name']
        self.root_dir = properties['root_dir']
        self.encoding = properties['encoding']
        self.data = properties['data']
        self.data.update({
            'name':self.name,
            'title': self.data.get('entry'),
            'isbn': '999999',
            'cssnames':list(),
            'htmlnames':list(),
            'imagenames':list(),
            })
        'parse toc data to get html filenames'
        self.get_htmlnames()
        'parse html filenames to get img and css filenames'
        self.get_image_css_names()
        
    def pack(self):
        ''' Follow the Epub spec:
                Make the mimetype file (standard, nothing special)
                Make the container file (ditto)
                Make the titlepage, uses the title and toc data 
                    created from the EpubRenderer.
                Make the opf file, uses the htmlnames, imagenames, cssnames from 
                    the initialization
                Make the ncx file, just like opf, except adding reading order
                    attributes (using template counters)
                Finally, zip everything together as the spec describes and 
                    create the *.epub file
            '''
        self.make_mimetype()
        self.make_container()
        self.make_titlepage()
        self.make_opf()
        self.make_ncx()
        #
        self.zip_ebook()
#        self.cleanup()
        
    def get_htmlnames(self):
        htmlnames = list()
        htmlnames.append(split_name(self.data.get('url')))#top-level file
        for subsection in self.data.get('subs', list()):
            htmlnames.append(split_name(subsection.get('url')))
            for subsubsection in subsection.get('subs', list()):
                htmlnames.append(split_name(subsubsection.get('url')))
                for subsubsubsection in subsubsection.get('subs', list()):
                    htmlnames.append(split_name(subsubsubsection.get('url')))
        self.data['htmlnames'] = htmlnames 

    def get_image_css_names(self):
        cssnames = list()
        imagenames = list()
        for fname in self.data['htmlnames']:
            if not fname['fullname']:
                fname['fullname'] = 'index.html'
#           print os.path.join(self.root_dir, fname['fullname'])
            parser = NameParser(os.path.join(self.root_dir, fname['fullname']), self.encoding)
            parser.parse()
            cssnames.extend(parser.get_cssnames())
            imagenames.extend(parser.get_imagenames())

        for cssname in set(cssnames):
            self.data['cssnames'].append(split_name(cssname))

        for imagename in set(imagenames):
            self.data['imagenames'].append(split_name(imagename))
            
    def make_mimetype(self):
        fd = open(os.path.join(self.root_dir, 'mimetype'), 'wb')
        fd.write(templates.mimetype)
        fd.close()

    def make_container(self):
        fd = open(os.path.join(self.root_dir, 'container.xml'), 'wb')
        fd.write(templates.container)
        fd.close()

    def make_titlepage(self):
        context = simpleTALES.Context()
        context.addGlobal('data', self.data)
        compiled = simpleTAL.compileXMLTemplate(templates.titlepage)

        fd0 = open(os.path.join(self.root_dir, 'titlepage.html'), 'wb')
        compiled.expand(context, fd0, outputEncoding=self.encoding,suppressXMLDeclaration=True)
        fd0.close()
        
    def make_opf(self):
        context = simpleTALES.Context()
        context.addGlobal('data', self.data)
        context.addGlobal('date', datetime.date.isoformat(datetime.date.today()))
        compiled = simpleTAL.compileXMLTemplate(templates.opf)

        fd = open(os.path.join(self.root_dir, 'content.opf'), 'wb')
        compiled.expand(context, fd, outputEncoding=self.encoding)
        fd.close()

    def make_ncx(self):
        context = simpleTALES.Context(allowPythonPath=1)
        context.addGlobal('data', self.data)
        compiled = simpleTAL.compileXMLTemplate(templates.ncx)

        fd = open(os.path.join(self.root_dir, 'toc.ncx'), 'wb')
        compiled.expand(context, fd, outputEncoding=self.encoding, docType=NCX_DOCTYPE)
        fd.close()

    def zip_ebook(self):
        z = zipfile.ZipFile(os.path.join(self.root_dir, '%s.epub' % self.data['name']), 'w')
        z.write(os.path.join(self.root_dir, 'mimetype'), arcname='mimetype')
        z.write(os.path.join(self.root_dir, 'container.xml'), arcname='META-INF/container.xml')

        for fname in ['content.opf', 'toc.ncx', 'titlepage.html']:
            z.write(os.path.join(self.root_dir, fname), arcname='OEBPS/%s' % fname)

        for namelist in [self.data['htmlnames'], self.data['imagenames']]:
            for fname in [x['fullname'] for x in namelist]:
                if fname.count('common.hlp'):
                    continue
                if os.path.isfile(os.path.join(self.root_dir, fname)):
                    z.write(os.path.join(self.root_dir, fname), arcname='OEBPS/%s' % fname)
        z.close()
        
    def cleanup(self):
        'Comment this method for debugging'
        for fname in ['mimetype',
                      'container.xml',
                      'content.opf',
                      'toc.ncx',
                      'titlepage.html',
                      'index.html',
                      ]:
            if os.path.exists(fname):
                os.unlink(os.path.join(self.root_dir, fname))

class EpubRenderer(XHTMLRenderer):
    ''' Class to parse document, using XHTML's machinery, but adds packaging
        to support the *.epub format. The cleanup method is called automatically
        and that's where we hook in the extra packaging in doEpubFiles.
        '''
    def doJavaHelpFiles(self, document, version):
        pass
    def doEclipseHelpFiles(self, document):
        pass
    def doCHMFiles(self, document):
        pass

    def doEpubFiles(self, document):
        ''' set up a properties dictionary using TOC data and some other
            defaults; then call the Epub_Package class to package everything up.
            '''
        tocdata = self.makeTOCData(document)

        properties = dict()
        properties['data'] = tocdata[0]
        properties['root_dir'] = os.getcwd()
        properties['encoding'] = 'utf-8'
        properties['name'] = document.userdata.get('jobname','index')

        package = Epub_Package(properties)
        package.pack()                  
        
    def cleanup(self, document, files, postProcess=None):
        res = XHTMLRenderer.cleanup(self, document, files, postProcess=postProcess)
        self.database = dict()
        self.doEpubFiles(document)
        return res
    
    def makeTOCData(self, document):
        ''' get the toc data from the document, return a list of dictionaries.
            each dictionary has a title, url and a list of subsections. Each
            subsection is a similar dictionary. nested down as far as the 
            actual table of contents in the doc.
            We want a nice toc for the ebook, and that's why we package multiple
            html files up instead of creating one monolithic html file.
            '''
        def addEntry(entry):
            entryList = list()
            for e in entry.fulltableofcontents:
                title = u'%s' % unicode(e.tocEntry.textContent)
                if title == 'Index':
                    break
                tocDict = {'chapter': document.userdata.get('jobname','index'),
                            'entry':title,
                            'url': u'%s' % unicode(e.url), }
                tocDict['subs'] = addEntry(e)
                entryList.append(tocDict)
            return entryList

        return addEntry(document.getElementsByTagName('document')[0])

class Epub(object):
    ''' simple class to initialize with the name of a tex document.
        controls plastex command-line-type options through config dict.
        parse method parses and renders the doc resulting in *.epub file
        '''
    def __init__(self, name):
        self.name = name
        self.filename = '%s.tex' % name
        self.config = config
        self.config['general']['renderer'] = 'Epub'
        self.config['general']['theme'] = 'default'

    def parse(self):
        self.doc = plasTeX.TeXDocument(config=self.config)
        self.tex = TeX(self.doc, file=self.filename)
        self.tex.parse()

        renderer = EpubRenderer()
        renderer.chapterName = self.name
        renderer.render(self.doc)
        
Renderer = EpubRenderer

if __name__ == '__main__':
    'set directory containing epub default template'
    os.environ['EPUBTEMPLATES'] = os.path.join('/Users',
                                               os.environ['USER'],
                                               'EPUBTEMPLATES',)
    os.environ['XHTMLTEMPLATES'] =  os.environ['EPUBTEMPLATES']
    book = Epub('sample2e')
    book.parse()

