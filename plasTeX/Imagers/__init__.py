#!/usr/bin/env python

import os, time, tempfile, shutil, re, string, pickle, codecs
try: from hashlib import md5
except ImportError: from md5 import new as md5
from plasTeX.Logging import getLogger
from StringIO import StringIO
from plasTeX.Filenames import Filenames
from plasTeX.dictutils import ordereddict
import subprocess
import shlex

log = getLogger()
depthlog = getLogger('render.images.depth')
status = getLogger('status')
imagelog = getLogger('imager')

try:
    import Image as PILImage
    import ImageChops as PILImageChops
except ImportError:
    PILImage = PILImageChops = None

def autoCrop(im, bgcolor=None, margin=0):
    """
    Automatically crop image down to non-background portion

    Required Argument:
    im -- image object

    Optional Argument:
    bgcolor -- value or tuple containing the color to use for the 
        background color when cropping
    margin -- leave this many pixels around the content.  If there
        aren't that many pixels to leave, leave as many as possible.

    Returns: cropped image object and tuple containing the number
        of pixels removed from each side (left, top, right, bottom) 

    """
    if im.mode != "RGB":
        im = im.convert("RGB")

    origbbox = im.getbbox()
    if origbbox is None:
        origbbox = (0,0,im.size[0],im.size[1])

    # Figure out the background color from the corners, if needed
    if bgcolor is None:
        topleft = im.getpixel((origbbox[0],origbbox[1]))
        topright = im.getpixel((origbbox[2]-1,origbbox[1]))
        bottomleft = im.getpixel((origbbox[0],origbbox[3]-1))
        bottomright = im.getpixel((origbbox[2]-1,origbbox[3]-1))
        corners = [topleft, topright, bottomleft, bottomright]

        matches = []
        matches.append(len([x for x in corners if x == topleft]))
        matches.append(len([x for x in corners if x == topright]))
        matches.append(len([x for x in corners if x == bottomleft]))
        matches.append(len([x for x in corners if x == bottomright]))

        try: bgcolor = corners[matches.index(1)]
        except ValueError: pass
        try: bgcolor = corners[matches.index(2)]
        except ValueError: pass
        try: bgcolor = corners[matches.index(3)]
        except ValueError: pass
        try: bgcolor = corners[matches.index(4)]
        except ValueError: pass

    # Create image with only the background color
    bg = PILImage.new("RGB", im.size, bgcolor)

    # Get bounding box of non-background content
    diff = PILImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if bbox:
        if margin:
            bbox = list(bbox)
            bbox[0] -= margin
            bbox[1] -= margin
            bbox[2] += margin
            bbox[3] += margin
            bbox = tuple([max(0,x) for x in bbox])
        return im.crop(bbox), tuple([abs(x-y) for x,y in zip(origbbox,bbox)]), bgcolor
    return PILImage.new("RGB", (1,1), bgcolor), (0,0,0,0), bgcolor
    return None, None, bgcolor # no contents

class Box(object):
    pass

class Dimension(float):
    """
    Dimension object used for width, height, and depth of images

    This object is simply a float value.  The value of the float 
    is in pixels.  All other units can be gotten using their 
    corresponding property.

    """
    fontSize = 15
    @property
    def ex(self): 
        return '%sex' % self.format(self / (self.fontSize * 0.6))
    @property
    def em(self): 
        return '%sem' % self.format(self / self.fontSize)
    @property
    def pt(self): 
        return '%spt' % self.format(self)
    @property
    def px(self): 
        return '%spx' % self.format(self)
    @property
    def mm(self): 
        return '%smm' % self.format(self.cm * 10.0)
    @property
    def inch(self): 
        return '%sin' % self.format(self.pt / 72.0)
    @property
    def cm(self): 
        return '%scm' % self.format(self.inch * 2.54)
    @property
    def pc(self): 
        return '%spc' % self.format(self.pt / 12.0)

    def __getattribute__(self, name):
        if name in ['in']:
            return self.inch
        return float.__getattribute__(self, name)

    def format(self, value):
        if abs(int(value) - value) < 0.0001:
            return '%s' % int(value)
        return '%0.3f' % value

    def __str__(self):
        return self.format(self)

    def __repr__(self):
        return self.format(self)
        

class DimensionPlaceholder(str):
    """ 
    Placeholder for dimensions

    Dimensions for an image aren't generally known until the end of
    the rendering process.  This object generates a placeholder
    for the dimension.

    """
    imageUnits = ''
    def __getattribute__(self, name):
        if name in ['in','ex','em','pt','px','mm','cm','pc']:
            if not self:
                return self
            vars = {'units':name}
            return self + string.Template(self.imageUnits).substitute(vars)
        return str.__getattribute__(self, name)
    def __setattribute__(self, name, value):
        if name in ['in','ex','em','pt','px','mm','cm','pc']:
            return 
        return str.__setattribute__(self, name, value)

class Image(object):
    """ Generic image object """

    def __init__(self, filename, config, width=None, height=None, alt=None,
                       depth=None, longdesc=None):
        self.filename = filename
        self.path = os.path.join(os.getcwd(), self.filename)
        self.width = width
        self.height = height
        self.alt = alt
        self.depth = depth
        self.depthRatio = 0
        self.longdesc = longdesc 
        self.config = config
        self._cropped = False
        self.bitmap = self
        self.checksum = None

    def height():
        def fget(self):
            return getattr(self.bitmap, '_height', None)
        def fset(self, value):
            if value is None:
                self._height = value
            elif isinstance(value, DimensionPlaceholder):
                self._height = value
            else:
                self._height = Dimension(value)
        return locals()
    height = property(**height())

    def width():
        def fget(self):
            return getattr(self.bitmap, '_width', None)
        def fset(self, value):
            if value is None:
                self._width = value
            elif isinstance(value, DimensionPlaceholder):
                self._width = value
            else:
                self._width = Dimension(value)
        return locals()
    width = property(**width())

    def depth():
        def fget(self):
            return getattr(self, '_depth', None)
        def fset(self, value):
            if value is None:
                self._depth = value
            elif isinstance(value, DimensionPlaceholder):
                self._depth = value
            else:
                self._depth = Dimension(value)
        return locals()
    depth = property(**depth())

    @property
    def url(self):
        base = self.config['base-url']
        if base and base.endswith('/'):
            base = base[:-1]
        if base:
            return '%s/%s' % (base, self.filename)
        return self.filename

    def crop(self):
        """ Do the actual cropping """
        if self._cropped:
            return

        # Crop an SVG image
        if os.path.splitext(self.path)[-1] in ['.svg']:
            svg = open(self.path,'r').read()

            self.width = 0
            width = re.search(r'width=(?:\'|")([^\d\.]+)\w*(?:\'|")', svg)
            if width:
                self.width = float(width)

            self.height = 0
            height = re.search(r'height=(?:\'|")([^\d\.]+)\w*(?:\'|")', svg)
            if height:
                self.height = float(height)

            self.depth = 0
            if self.bitmap and self.height:
                depth = (self.height / self.bitmap.height) * self.bitmap.depth
                if abs(depth - int(depth)) > 0.1:
                    self.depth = depth - 1
                else:
                    self.depth = depth
                
            self._cropped = True
            return

        padbaseline = self.config['baseline-padding']

        try:
            im, self.depth = self._stripBaseline(PILImage.open(self.path), 
                                             padbaseline)
            self.width, self.height = im.size
        except IOError, msg:
#           import traceback
#           traceback.print_exc()
            self._cropped = True
            log.warning(msg)
            return

        if padbaseline and self.depth > padbaseline:
            log.warning('depth of image %s (%d) is greater than the baseline padding (%s).  This may cause the image to be misaligned with surrounding text.', self.filename, self.depth, padbaseline)

        if self.config['transparent']:
            im = im.convert("P")
            lut = im.resize((256,1))
            lut.putdata(range(256))
            index = list(lut.convert("RGB").getdata()).index((255,255,255))
            im.save(self.path, transparency=index)
        else:
            im.save(self.path)

        self._cropped = True

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename

    def _autoCrop(self, im, bgcolor=None, margin=0):
        return autoCrop(im, bgcolor, margin)

    def _stripBaseline(self, im, padbaseline=0):
        """
        Find the baseline register mark and crop it out

        The image has to have a particular layout.  The top left corner
        must be the background color of the image.  There should be a
        square registration mark which has the bottom edge at the baseline
        of the image (see \\plasTeXregister in LaTeX code at the top
        of this file).  This registration mark should be the leftmost 
        content of the image.  If the registration mark is at the top
        of the image, the baseline is ignored.

        Required Arguments:
        im -- image to be cropped

        Keyword Arguments:
        padbaseline -- amount to pad the bottom of all cropped images.
            This allows you to use one margin-bottom for all images;
            however, you need to make sure that this padding is large 
            enough to handle the largest descender in the document.

        Returns:
        (cropped image, distance from baseline to bottom of image)

        """
        if im.mode != "RGB":
            im = im.convert("RGB")

        depth = 0

        # Crop the image so that the regitration mark is on the left edge
        im, box, background = self._autoCrop(im)

        width, height = im.size
        
        # Determine if registration mark is at top or left
        top = False
        # Found mark at top
        if im.getpixel((0,0)) != background:
            top = True
            i = 1
            # Parse past the registration mark
            # We're fudging the vertical position by 1px to catch 
            # things sitting right under the baseline.
            while i < width and im.getpixel((i,1)) != background:
                i += 1
            # Look for additional content after mark
            if i < width:
                while i < width and im.getpixel((i,1)) == background:
                    i += 1
                # If there is non-background content after mark,
                # consider the mark to be on the left
                if i < width:
                    top = False

        # Registration mark at the top
        blank = False
        if top:
            pos = height - 1
            while pos and im.getpixel((0,pos)) == background:
                pos -= 1
            depth = pos - height + 1

            # Get the height of the registration mark so it can be cropped out
            rheight = 0
            while rheight < height and im.getpixel((0,rheight)) != background:
                rheight += 1

            # If the depth is the entire height, just make depth = 0
            if -depth == (height-rheight):
                depth = 0

            # Handle empty images
            bbox = im.getbbox()
            if bbox is None or rheight == (height-1):
                blank = True
            else:
                bbox = list(bbox)
                bbox[1] = rheight

        # Registration mark on left side
        if blank or not(top) or im.getbbox()[1] == 0:
            pos = height - 1
            while pos and im.getpixel((0,pos)) == background:
                pos -= 1
            depth = pos - height + 1

            # Get the width of the registration mark so it can be cropped out
            rwidth = 0
            while rwidth < width and im.getpixel((rwidth,pos)) != background:
                rwidth += 1

            # Handle empty images
            bbox = im.getbbox()
            if bbox is None or rwidth == (width-1):
                return PILImage.new("RGB", (1,1), background), 0

            bbox = list(bbox)
            bbox[0] = rwidth

        # Crop out register mark, and autoCrop result    
        im, cropped, background = self._autoCrop(im.crop(bbox), background)

        # If the content was entirely above the baseline, 
        # we need to keep that whitespace
        depth += cropped[3]
        depthlog.debug('Depth of image %s is %s', self.filename, depth)

        # Pad all images with the given amount.  This allows you to 
        # set one margin-bottom for all images.
        if padbaseline:
            width, height = im.size
            newim = PILImage.new("RGB", (width,height+(padbaseline+depth)), background)
            newim.paste(im, im.getbbox())
            im = newim

        return im, depth
    

class Imager(object):
    """ Generic Imager """

    # The command to run on the LaTeX output file to generate images.
    # This should be overridden by the subclass.
    command = ''

    # The compiler command used to compile the LaTeX document
    compiler = 'latex'

    # Verification command to determine if the imager is available
    verification = ''

    fileExtension = '.png'

    imageAttrs = ''
    imageUnits = ''

    def __init__(self, document, imageTypes=None):
        self.config = document.config
        self.ownerDocument = document

        if imageTypes is None:
            self.imageTypes = [self.fileExtension]
        else:
            self.imageTypes = imageTypes[:]

        # Dictionary that makes sure each image is only generated once.
        # The key is the LaTeX source and the value is the image instance.
        self._cache = {}
        usednames = {}
        self._filecache = os.path.abspath(os.path.join('.cache', 
                                          self.__class__.__name__+'.images'))
        if self.config['images']['cache'] and os.path.isfile(self._filecache):
            try: 
                self._cache = pickle.load(open(self._filecache, 'r'))
                for key, value in self._cache.items():
                    if not os.path.isfile(value.filename):
                        del self._cache[key]
                        continue
                    usednames[value.filename] = None
            except ImportError:
                os.remove(self._filecache)

        # List of images in the order that they appear in the LaTeX file
        self.images = ordereddict()

        # Images that are simply copied from the source directory
        self.staticimages = ordereddict()

        # Filename generator
        self.newFilename = Filenames(self.config['images'].get('filenames', raw=True), 
                           vars={'jobname':document.userdata.get('jobname','')},
                           extension=self.fileExtension, invalid=usednames)

        # Start the document with a preamble
        self.source = StringIO()
        self.source.write('\\scrollmode\n')
        self.writePreamble(document)
        self.source.write('\\begin{document}\n')

        # Set up additional options
        self._configOptions = self.formatConfigOptions(self.config['images'])

    def formatConfigOptions(self, config):
        """
        Format configuration options as command line options

        Required Arguments:
        config -- the images section of the configuration object

        Returns: a list of two-element tuples contain option value pairs 

        Example::
            output = []
            if config['resolution']:
                output.append(('-D', config['resolution']))
            return output

        """
        return []

    def writePreamble(self, document):
        """ Write any necessary code to the preamble of the document """
        self.source.write(document.preamble.source)
        self.source.write('\\makeatletter\\oddsidemargin -0.25in\\evensidemargin -0.25in\n')

#       self.source.write('\\tracingoutput=1\n')
#       self.source.write('\\tracingonline=1\n')
#       self.source.write('\\showboxbreadth=\maxdimen\n')
#       self.source.write('\\showboxdepth=\maxdimen\n')
#       self.source.write('\\newenvironment{plasTeXimage}[1]{\\def\\@current@file{#1}\\thispagestyle{empty}\\def\\@eqnnum{}\\setbox0=\\vbox\\bgroup}{\\egroup\\typeout{imagebox:\\@current@file(\\the\\ht0+\\the\\dp0)}\\box0\\newpage}')

        self.source.write('\\@ifundefined{plasTeXimage}{'
                          '\\newenvironment{plasTeXimage}[1]{' +
                          '\\vfil\\break\\plasTeXregister' +
                          '\\thispagestyle{empty}\\def\\@eqnnum{}\\def\\tagform@{\\@gobble}' +
                          '\\ignorespaces}{}}{}\n')
        self.source.write('\\@ifundefined{plasTeXregister}{' +
                          '\\def\\plasTeXregister{\\parindent=-0.5in\\ifhmode\\hrule' +
                          '\\else\\vrule\\fi height 2pt depth 0pt ' +
                          'width 2pt\\hskip2pt}}{}\n')

    def verify(self):
        """ Verify that this commmand works on this machine """
        if self.verification:
            proc = os.popen(self.verification)
            proc.read()
            if not proc.close():
                return True
            return False

        if not self.command.strip():
            return False

        cmd = self.command.split()[0]

        if not cmd:
            return False

        proc = os.popen('%s --help' % cmd)
        proc.read()
        if not proc.close():
            return True

        return False

    @property
    def enabled(self):
        if self.config['images']['enabled'] and \
           (self.command or (type(self) is not Imager and type(self) is not VectorImager)): 
            return True
        return False

    def close(self):
        """ Invoke the rendering code """
        # Finish the document
        self.source.write('\n\\end{document}\\endinput')

        for value in self._cache.values():
            if value.checksum and os.path.isfile(value.path):
                 d = md5(open(value.path,'r').read()).digest()
                 if value.checksum != d:
                     log.warning('The image data for "%s" on the disk has changed.  You may want to clear the image cache.' % value.filename)

        # Bail out if there are no images
        if not self.images:
            return 

        if not self.enabled:
            return

        # Compile LaTeX source, then convert the output
        self.source.seek(0)
        output = self.compileLatex(self.source.read())
        if output is None:
            log.error('Compilation of the document containing the images failed.  No output file was found.')
            return

        self.convert(output)

        for value in self._cache.values():
            if value.checksum is None and os.path.isfile(value.path):
                 value.checksum = md5(open(value.path,'r').read()).digest()

        if not os.path.isdir(os.path.dirname(self._filecache)):
            os.makedirs(os.path.dirname(self._filecache))
        pickle.dump(self._cache, open(self._filecache,'w'))

    def compileLatex(self, source):
        """
        Compile the LaTeX source

        Arguments:
        source -- the LaTeX source to compile

        Returns:
        file object corresponding to the output from LaTeX

        """
        cwd = os.getcwd()

        # Make a temporary directory to work in
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        filename = 'images.tex'

        # Write LaTeX source file
        if self.config['images']['save-file']:
            self.source.seek(0)
            codecs.open(os.path.join(cwd,filename), 'w', self.config['files']['input-encoding']).write(self.source.read())
        self.source.seek(0)
        codecs.open(filename, 'w', self.config['files']['input-encoding']).write(self.source.read())

        # Run LaTeX
        os.environ['SHELL'] = '/bin/sh'
        program = self.config['images']['compiler']
        if not program:
            program = self.compiler

        cmd = r'%s %s' % (program, filename)
        p = subprocess.Popen(shlex.split(cmd),
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     )
        while True:
            line = p.stdout.readline()
            done = p.poll()
            if line:
                imagelog.info(str(line.strip()))        
            elif done is not None:
                break

        output = None
        for ext in ['.dvi','.pdf','.ps']:
            if os.path.isfile('images'+ext):
                output = WorkingFile('images'+ext, 'rb', tempdir=tempdir)
                break

        # Change back to original working directory
        os.chdir(cwd)

        return output

    def executeConverter(self, output):
        """ 
        Execute the actual image converter 

        Arguments:
        output -- file object pointing to the rendered LaTeX output

        Returns:
        two-element tuple.  The first element is the return code of the
        command.  The second element is the list of filenames generated.
        If the default filenames (i.e. img001.png, img002.png, ...) are
        used, you can simply return None.

        """
        open('images.out', 'wb').write(output.read())
        options = ''
        if self._configOptions:
            for opt, value in self._configOptions:
                opt, value = str(opt), str(value)
                if ' ' in value:
                    value = '"%s"' % value
                options += '%s %s ' % (opt, value)

        cmd = r'%s %s%s' % (self.command, options, 'images.out')
        p = subprocess.Popen(shlex.split(cmd),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                           )
        done = None
        while True:
            line = p.stdout.readline()
            done = p.poll()
            if line:
                imagelog.info(str(line.strip()))        
            elif done is not None:
                break
        return done, None

    def convert(self, output):
        """
        Convert the output from LaTeX into images

        Arguments:
        output -- output file object

        """
        if not self.command and self.executeConverter is Imager.executeConverter:
            log.warning('No imager command is configured.  ' +
                        'No images will be created.')
            return

        cwd = os.getcwd()

        # Make a temporary directory to work in
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        # Execute converter
        rc, images = self.executeConverter(output)
        if rc:
            log.warning('Image converter did not exit properly.  ' +
                        'Images may be corrupted or missing.')

        # Get a list of all of the image files
        if images is None:
            images = [f for f in os.listdir('.') 
                            if re.match(r'^img\d+\.\w+$', f)]
        if len(images) != len(self.images):
            log.warning('The number of images generated (%d) and the number of images requested (%d) is not the same.' % (len(images), len(self.images)))

        # Sort by creation date
        #images.sort(lambda a,b: cmp(os.stat(a)[9], os.stat(b)[9]))

        images.sort(lambda a,b: cmp(int(re.search(r'(\d+)\.\w+$',a).group(1)), 
                                    int(re.search(r'(\d+)\.\w+$',b).group(1))))

        os.chdir(cwd)

        if PILImage is None:
            log.warning('PIL (Python Imaging Library) is not installed.  ' +
                        'Images will not be cropped.')
            
        # Move images to their final location
        for src, dest in zip(images, self.images.values()):
            # Move the image
            directory = os.path.dirname(dest.path)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory)
            try:
                shutil.copy2(os.path.join(tempdir,src), dest.path)
            except OSError:
                shutil.copy(os.path.join(tempdir,src), dest.path)

            # Crop the image
            try: 
                dest.crop()
                status.dot()
            except Exception, msg:
                import traceback
                traceback.print_exc()
                log.warning('failed to crop %s (%s)', dest.path, msg)
        
        # Remove temporary directory
        shutil.rmtree(tempdir, True)

    def writeImage(self, filename, code, context):
        """
        Write LaTeX source for the image

        Arguments:
        filename -- the name of the file that will be generated
        code -- the LaTeX code of the image
        context -- the LaTeX code of the context of the image

        """
        self.source.write('%s\n\\begin{plasTeXimage}{%s}\n%s\n\\end{plasTeXimage}\n' % (context, filename, code))

    def newImage(self, text, context='', filename=None):
        """ 
        Invoke a new image 

        Required Arguments:
        text -- the LaTeX source to be rendered in an image
        
        Keyword Arguments:
        context -- LaTeX source to be executed before the image
            is created.  This generally consists of setting counters,
            lengths, etc. that will be used by the code that
            generates the image.
        filename -- filename to force the image to.  This filename
            should not include the file extension. 

        """
        # Convert ligatures back to original string
        for dest, src in self.ownerDocument.charsubs:
            text = text.replace(src, dest)

        key = text

        # See if this image has been cached
        if self._cache.has_key(key):
            return self._cache[key]
            
        # Generate a filename
        if not filename:
            filename = self.newFilename()

        # Add the image to the current document and cache
        #log.debug('Creating %s from %s', filename, text)
        self.writeImage(filename, text, context)

        img = Image(filename, self.config['images'])

        # Populate image attrs that will be bound later
        if self.imageAttrs:
            tmpl = string.Template(self.imageAttrs)
            vars = {'filename':filename}
            for name in ['height','width','depth']:
                if getattr(img, name) is None:
                    vars['attr'] = name
                    value = DimensionPlaceholder(tmpl.substitute(vars))
                    value.imageUnits = self.imageUnits
                    setattr(img, name, value)
    
        self.images[filename] = self._cache[key] = img
        return img

    def getImage(self, node):
        """
        Get an image from the given node whatever way possible

        This method attempts to find an existing image using the
        `imageoverride' attribute.  If it finds it, the image is 
        converted to the appropriate output format and copied to the
        images directory.  If no image is available, or there was
        a problem in getting the image, an image is generated.

        Arguments:
        node -- the node to create the image from

        Returns:
        Image instance

        """
        name = getattr(node, 'imageoverride', None)
        if name is None:
            return self.newImage(node.source)

        if name in self.staticimages:
            return self.staticimages[name]

        # Copy or convert the image as needed
        path = self.newFilename()
        newext = os.path.splitext(path)[-1]
        oldext = os.path.splitext(name)[-1]
        try:
            directory = os.path.dirname(path)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory)

            # If PIL isn't available or no conversion is necessary, 
            # just copy the image to the new location
            if newext == oldext or oldext in self.imageTypes:
                path = os.path.splitext(path)[0] + os.path.splitext(name)[-1]
                if PILImage is None:
                    shutil.copyfile(name, path)
                    tmpl = string.Template(self.imageAttrs)
                    width = DimensionPlaceholder(tmpl.substitute({'filename':path, 'attr':'width'}))
                    height = DimensionPlaceholder(tmpl.substitute({'filename':path, 'attr':'height'}))
                    height.imageUnits = width.imageUnits = self.imageUnits
                else:
                    img = PILImage.open(name)
                    width, height = img.size
                    scale = self.config['images']['scale-factor']
                    if scale != 1:
                        width = int(width * scale)
                        height = int(height * scale)
                        img.resize((width,height))
                        img.save(path)
                    else:
                        shutil.copyfile(name, path)
                    
            # If PIL is available, convert the image to the appropriate type
            else:
                img = PILImage.open(name)
                width, height = img.size
                scale = self.config['images']['scale-factor']
                if scale != 1:
                    width = int(width * scale)
                    height = int(height * scale)
                    img.resize((width,height))
                img.save(path)
            img = Image(path, self.ownerDocument.config['images'], width=width, height=height)
            self.staticimages[name] = img
            return img

        # If anything fails, just let the imager handle it...
        except Exception, msg:
            #log.warning('%s in image "%s".  Reverting to LaTeX to generate the image.' % (msg, name))
            pass
        return self.newImage(node.source)


class VectorImager(Imager):
    fileExtension = '.svg'

    def writePreamble(self, document):
        Imager.writePreamble(self, document)
#       self.source.write('\\usepackage{type1ec}\n')
        self.source.write('\\def\\plasTeXregister{}\n')


class WorkingFile(file):
    """
    File used for processing in a temporary directory

    When the file is closed or the object is deleted, the temporary
    directory associated with the file is deleted as well.

    """

    def __init__(self, *args, **kwargs):
        if 'tempdir' in kwargs:
            self.tempdir = kwargs['tempdir']
            del kwargs['tempdir']
        file.__init__(self, *args, **kwargs)

    def close(self):
        if self.tempdir and os.path.isdir(self.tempdir):
            shutil.rmtree(self.tempdir, True)
        file.close(self)

    def __del__(self):
        self.close()

