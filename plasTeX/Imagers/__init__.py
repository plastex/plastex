#!/usr/bin/env python

import os, time, tempfile, shutil, re, string
from plasTeX.Logging import getLogger
from StringIO import StringIO
from plasTeX.Filenames import Filenames
from plasTeX.dictutils import ordereddict

log = getLogger()
depthlog = getLogger('render.images.depth')

try:
    import Image as PILImage
    import ImageChops as PILImageChops
except ImportError:
    PILImage = PILImageChops = None


class Image(object):
    """ Generic image object """

    def __init__(self, filename, config, width=None, height=None, alt=None,
                       depth=0, longdesc=None):
        self.filename = filename
        self.path = os.path.join(os.getcwd(), self.filename)
        self.width = width
        self.height = height
        self.alt = alt
        self.depth = depth
        self.longdesc = longdesc 
        self.config = config
        self._cropped = False

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

        padbaseline = self.config['baseline-padding']

        try:
            im, self.depth = self._stripbaseline(PILImage.open(self.path), 
                                                 padbaseline)
            self.width, self.height = im.size
        except IOError, msg:
            self._cropped = True
            log.warning(msg)
            return

        if padbaseline and self.depth > padbaseline:
            log.warning('depth of image %s (%d) is greater than the baseline padding (%s).  This may cause the image to be misaligned with surrounding text.', self.filename, self.depth, padbaseline)
        im.save(self.path)
        self._cropped = True

    def __str__(self):
        return self.filename

    def __repr__(self):
        return self.filename

    def _autocrop(self, im, bgcolor=None):
        """
        Automatically crop image down to non-background portion

        Required Argument:
        im -- image object

        Optional Argument:
        bgcolor -- value or tuple containing the color to use for the 
            background color when cropping

        Returns: cropped image object and tuple containing the number
            of pixels removed from each side (left, top, right, bottom) 

        """
        if im.mode != "RGB":
            im = im.convert("RGB")

        origbbox = im.getbbox()

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
            return im.crop(bbox), tuple([abs(x-y) for x,y in zip(origbbox,bbox)])
        return None, None # no contents

    def _stripbaseline(self, im, padbaseline=0):
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
        background = im.getpixel((0,0))

        # Crop the image so that the regitration mark is on the left edge
        im = self._autocrop(im)[0]

        width, height = im.size

        # Registration mark at the top
        if im.getpixel((0,0)) != background:
            depth = 0
            pos = 0

        else:
            pos = height - 1
            while pos and im.getpixel((0,pos)) == background:
                pos -= 1
            depth = pos - height + 1

        # Get the width of the registration mark so it can be cropped out
        foreground = im.getpixel((0,pos))
        rwidth = 0
        while rwidth < width and im.getpixel((rwidth,pos)) == foreground:
            rwidth += 1

        # Handle empty images
        bbox = im.getbbox()
        if bbox is None:
            return PILImage.new("RGB", (1,1), background), 0

        # Crop out register mark, and autocrop result
        bbox = list(bbox)
        bbox[0] = rwidth
        im, cropped = self._autocrop(im.crop(bbox), background)

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

    fileextension = ''

    imageattrs = ''

    def __init__(self, document):
        self.config = document.config['images']
        self.ownerDocument = document

        # Dictionary that makes sure each image is only generated once.
        # The key is the LaTeX source and the value is the image instance.
        self._cache = {}

        # List of images in the order that they appear in the LaTeX file
        self.images = ordereddict()

        # Images that are simply copied from the source directory
        self.staticimages = ordereddict()

        # Filename generator
        self.newfilename = Filenames(self.config.get('filenames', raw=True), vars={'jobname':document.userdata.get('jobname','')}, extension=self.fileextension)

        # Start the document with a preamble
        self.source = StringIO()
        self.source.write('\\scrollmode\n')
        self.writepreamble(document)
        self.source.write('\\begin{document}\n')

    def writepreamble(self, document):
        """ Write any necessary code to the preamble of the document """
        self.source.write(document.preamble.source)
        self.source.write('\\makeatletter\n')
        self.source.write('\\@ifundefined{plasTeXimage}{\\newenvironment' +
                          '{plasTeXimage}[1]{\\vfil\\break\\plasTeXregister' +
                          '\\ignorespaces}{}}{}\n')
        self.source.write('\\@ifundefined{plasTeXregister}{' +
                          '\\def\\plasTeXregister{\\ifhmode\\hrule' +
                          '\\else\\vrule\\fi height 2pt depth 0pt ' +
                          'width 2pt\\hskip2pt}}{}\n')
        self.source.write('\\pagestyle{empty}\n')

    def verify(self):
        """ Verify that this commmand works on this machine """
        os.environ['SHELL'] = 'sh'
        if self.verification:
            if not os.system('%s >/dev/null 2>/dev/null' % self.verification):
                return True

        cmd = self.command.split()[0]

        if not cmd:
            return False

        if not os.system('%s --help >/dev/null 2>/dev/null' % cmd):
            return True

        return False

    def close(self):
        """ Invoke the rendering code """
        # Finish the document
        self.source.write('\n\\end{document}\\endinput')

        # Bail out if there are no images
        if not self._cache:
            return 

        if not self.config['enabled']:
            return

        # Compile LaTeX source, then convert the output
        self.source.seek(0)
        self.convert(self.compilelatex(self.source.read()))

    def compilelatex(self, source):
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
        self.source.seek(0)
#       print self.source.read()
#       open(os.path.join(cwd,filename), 'w').write(self.source.read())
#       self.source.seek(0)
        open(filename, 'w').write(self.source.read())

        # Run LaTeX
        os.environ['SHELL'] = '/bin/sh'
        program = self.config['compiler']
        if not program:
            program = self.compiler
        os.system(r"%s %s" % (program, filename))

        output = None
        for ext in ['.dvi','.pdf','.ps']:
            if os.path.isfile('images'+ext):
                output = WorkingFile('images'+ext, 'rb', tempdir=tempdir)
                break

        # Change back to original working directory
        os.chdir(cwd)

        return output

    def executeconverter(self, output):
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
        return os.system('%s %s' % (self.command, 'images.out')), None

    def convert(self, output):
        """
        Convert the output from LaTeX into images

        Arguments:
        output -- output file object

        """
        if not self.command:
            log.warning('No imager command is configured.  ' +
                        'No images will be created.')
            return

        cwd = os.getcwd()

        # Make a temporary directory to work in
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        # Execute converter
        rc, images = self.executeconverter(output)
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
        images.sort(lambda a,b: cmp(os.stat(a)[9], os.stat(b)[9]))

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
            shutil.copy2(os.path.join(tempdir,src), dest.path)

            # Crop the image
            try: 
                dest.crop()
            except Exception, msg:
                log.warning('failed to crop %s (%s)', dest.path, msg)
        
        # Remove temporary directory
        shutil.rmtree(tempdir, True)

    def writeimage(self, filename, code, context):
        """
        Write LaTeX source for the image

        Arguments:
        filename -- the name of the file that will be generated
        code -- the LaTeX code of the image
        context -- the LaTeX code of the context of the image

        """
        self.source.write('%s\n\\begin{plasTeXimage}{%s}\n%s\n\\end{plasTeXimage}\n' % (context, filename, code))

    def newimage(self, text, context='', filename=None):
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

        key = (text, context)

        # See if this image has been cached
        if self._cache.has_key(key):
            return self._cache[key]

        # Generate a filename
        if not filename:
            filename = self.newfilename()

        # Add the image to the current document and cache
        #log.debug('Creating %s from %s', filename, text)
        self.writeimage(filename, text, context)

        img = Image(filename, self.config)

        # Populate image attrs that will be bound later
        if self.imageattrs:
            tmpl = string.Template(self.imageattrs)
            vars = {'filename':filename}
            for name in ['height','width','depth']:
                if getattr(img, name) is None:
                    vars['attr'] = name
                    setattr(img, name, tmpl.substitute(vars))
    
        self.images[filename] = self._cache[key] = img
        return img

    def getimage(self, node):
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
            return self.newimage(node.source)

        if name in self.staticimages:
            return self.staticimages[name]

        # Copy or convert the image as needed
        path = self.newfilename()
        newext = os.path.splitext(path)[-1]
        oldext = os.path.splitext(name)[-1]
        try:
            # If PIL isn't available or no conversion is necessary, 
            # just copy the image to the new location
            if newext == oldext or oldext in self.imagetypes:
                path = os.path.splitext(path)[0] + os.path.splitext(name)[-1]
                shutil.copyfile(name, path)
                if PILImage is None:
                    tmpl = string.Template(self.imageattrs)
                    width = tmpl.substitute({'filename':path, 'attr':'width'})
                    height = tmpl.substitute({'filename':path, 'attr':'height'})
                else:
                    img = PILImage.open(name)
                    width, height = img.size
            # If PIL is available, convert the image to the appropriate type
            else:
                img = PILImage.open(name)
                width, height = img.size
                img.save(path)
            img = Image(path, self.ownerDocument.config['images'], width=width, height=height)
            self.staticimages[name] = img
            return img

        # If anything fails, just let the imager handle it...
        except Exception, msg:
            log.warning(msg)

        return self.newimage(img.source)


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

