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

from plasTeX.Imagers import WorkingFile

import plasTeX.Imagers

log = getLogger()
depthlog = getLogger('render.images.depth')
status = getLogger('status')
imagelog = getLogger('imager')

class Tralics(plasTeX.Imagers.Imager):
    """ Imager that uses dvipng """
    command = 'tralics'

    compiler = 'tralics'

    fileExtension = '.xml'

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
        self.newFilename = Filenames(self.config['images'].get('filenames', 
                                                               raw=True), 
                           vars={'jobname':document.userdata.get('jobname','')},
                           extension=self.fileExtension, invalid=usednames)

        # Start the document with a preamble
        self.source = StringIO()
        self.source.write('\\scrollmode\n')
        self.writePreamble(document)
        self.source.write('\\begin{document}\n')

        # Set up additional options
        self._configOptions = self.formatConfigOptions(self.config['images'])

    def writePreamble(self, document):
        """ Write any necessary code to the preamble of the document """
        self.source.write(document.preamble.source)

    def compileLatex(self, source):
        """
        Compile the LaTeX source

        Arguments:
        source -- the LaTeX source to compile

        Returns:
        file object corresponding to the output from LaTeX

        """
        print 'compileLatex'
        cwd = os.getcwd()

        # Make a temporary directory to work in
        tempdir = tempfile.mkdtemp()
        print 'tempdir', tempdir
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
        print 'cmd', cmd
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
        for ext in ['.xml']:
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
        print 'executeConverter'
        i = 1
        filenames = []
        for line in output:
            # TODO(downey): parse the XML and pick out the <math> tag
            if line.startswith('<formula'):
                filename = 'img%3.3d.xml' % i
                filenames.append(filename)
                print filename
                print line
                open(filename, 'wb').write(line)
                i += 1
        return 0, filenames

Imager = Tralics
