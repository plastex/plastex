#!/usr/bin/env python

import unittest, re, os, tempfile, shutil, glob, difflib, subprocess
from unittest import TestCase

class Process(object):
    """ Simple subprocess wrapper """
    def __init__(self, *args, **kwargs):
        if 'stdin' not in kwargs:
            kwargs['stdin'] = subprocess.PIPE
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.STDOUT
        self.process = subprocess.Popen(args, **kwargs)
        self.log = self.process.stdout.read()
        self.returncode = self.process.returncode
        self.process.stdout.close()
        self.process.stdin.close()

class Benched(TestCase):
    """ Compile LaTeX file and compare to benchmark file """

    filename = None

    def runTest(self):
        if not self.filename:
            return
            
        src = self.filename
        root = os.path.dirname(os.path.dirname(src))

        # Create temp dir and files
        outdir = tempfile.mkdtemp()
        texfile = os.path.join(outdir, os.path.basename(src))
        shutil.copyfile(src, texfile)

        # Run preprocessing commands
        for line in open(src):
            if line.startswith('%*'):
                command = line[2:].strip()
                p = Process(cwd=outdir, *command.split())
                if p.returncode:
                    raise OSError, 'Preprocessing command exited abnormally with return code %s: %s' % (command, p.log) 
            elif line.startswith('%#'):
                filename = line[2:].strip()
                shutil.copyfile(os.path.join(root,'extras',filename),
                                os.path.join(outdir,filename))
            elif line.startswith('%'):
                continue
            elif not line.strip():
                continue
            else:
                break

        # Run plastex
        outfile = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0]+'.html')
        p = Process('plastex','--split-level=0','--no-theme-extras',
                    '--dir=%s' % outdir,'--theme=minimal',
                    '--filename=%s' % os.path.basename(outfile), os.path.basename(src),
                    cwd=outdir)
        if p.returncode:
            shutil.rmtree(outdir, ignore_errors=True)
            raise OSError, 'plastex failed with code %s: %s' % (p.returncode, p.log)

        # Read output file
        output = open(outfile)

        # Get name of output file / benchmark file
        benchfile = os.path.join(root,'benchmarks',os.path.basename(outfile))
        if os.path.isfile(benchfile):
            bench = open(benchfile).readlines()
            output = output.readlines()
        else:
            try: os.makedirs(os.path.join(root,'new'))
            except: pass
            newfile = os.path.join(root,'new',os.path.basename(outfile))
            open(newfile,'w').write(output.read())
            shutil.rmtree(outdir, ignore_errors=True)
            raise OSError, 'No benchmark file: %s' % benchfile

        # Compare files
        diff = ''.join(list(difflib.unified_diff(bench, output))).strip()
        if diff:
            shutil.rmtree(outdir, ignore_errors=True)
            try: os.makedirs(os.path.join(root,'new'))
            except: pass
            newfile = os.path.join(root,'new',os.path.basename(outfile))
            open(newfile,'w').writelines(output)
            assert not(diff), 'Differences were found: %s' % diff

        # Clean up
        shutil.rmtree(outdir, ignore_errors=True)
                
def testSuite():
    """ Locate all .tex files and create a test suite from them """
    suite = unittest.TestSuite()
    for root, dirs, files in os.walk('.'):
        for f in files:
            if os.path.splitext(f)[-1] != '.tex':
                continue
            test = Benched()
            test.filename = os.path.abspath(os.path.join(root, f))
            suite.addTest(test)
    return suite

def test():
    """ Execute test suite """
    unittest.TextTestRunner().run(testSuite())

if __name__ == '__main__':
    test()

