"""
This file runs end-to-end tests by compiling full TeX files and comparing
with reference output files.
The folder containing this test file and each of its subfolder contains a
"sources" folder for TeX inputs, an optional "extras" folder for auxilliary
input, and a "benchmarks" folder containing the expected outputs.

Each input TeX file can start with the following species of special lines:
%* command to run     which runs a command before compilation
%# filename           which copies extras/filename to the output folder
                      before compilation
%python 3.X           which skips the test if python is older than 3.X


Each time such a test fails, the output is placed into a "new" folder.
This allows both easy comparison and replacement of the benchmark in
case the change is desired.
"""

import sys, os, shutil, difflib, subprocess
from pathlib import Path
import pytest


def which(name, path=None, exts=('',)):
    """
    Search PATH for a binary.

    Args:
    name -- the filename to search for
    path -- the optional path string (default: os.environ['PATH')
    exts -- optional list/tuple of extensions to try (default: ('',))

    Returns:
    The abspath to the binary or None if not found.
    """
    path = os.environ.get('PATH', path)
    for dir in path.split(os.pathsep):
        for ext in exts:
            binpath = os.path.abspath(os.path.join(dir, name) + ext)
            if os.path.isfile(binpath):
                return binpath
    return None

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
        self.log = self.process.stdout.read().decode('utf8')
        self.process.wait()
        self.returncode = self.process.returncode
        self.process.stdout.close()
        self.process.stdin.close()

files = [path for path in Path(__file__).parent.glob('**/*.tex')
         if 'sources' in path.parts]

@pytest.mark.parametrize('src', files,
                         ids=lambda p: p.name)
def test_benchmark(src, tmpdir):
    tmpdir = Path(str(tmpdir)) # For old python
    root = src.parent.parent

    # Create temp dir and files
    texfile = tmpdir/src.name
    shutil.copyfile(str(src), str(texfile))
    outdir = str(tmpdir)

    # Run preprocessing commands
    with src.open() as fh:
        for line in fh:
            if line.startswith('%*'):
                command = line[2:].strip()
                p = Process(cwd=outdir, *command.split())
                if p.returncode:
                    raise OSError('Preprocessing command exited abnormally with return code %s: %s' % (command, p.log))
            elif line.startswith('%#'):
                filename = line[2:].strip()
                (tmpdir / filename).parent.mkdir(exist_ok=True, parents=True)
                shutil.copyfile(str(root/'extras'/filename),
                                str(tmpdir/filename))
            elif line.startswith('%python '):
                # skip this test on old python
                version = tuple(int(n) for n in line[8:].strip().split('.'))
                if sys.version_info < version:
                    pytest.skip('This python is too old')
            elif line.startswith('%'):
                continue
            elif not line.strip():
                continue
            else:
                break

    # Run plastex
    outfile = (tmpdir/src.name).with_suffix('.html')
    plastex = which('plastex') or 'plastex'
    python = sys.executable
    p = Process(python, plastex,'--renderer=HTML5',
                '--split-level=0','--no-theme-extras',
                '--dir=%s' % outdir,'--theme=minimal',
                '--filename=%s' % outfile.name, src.name,
                cwd=outdir)
    if p.returncode:
        shutil.rmtree(outdir, ignore_errors=True)
        raise OSError('plastex failed with code %s: %s' % (p.returncode, p.log))

    benchfile = root/'benchmarks'/outfile.name
    if benchfile.exists():
        bench = benchfile.read_text().split('\n')
        output = outfile.read_text().split('\n')
    else:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/outfile.name))
        shutil.rmtree(outdir, ignore_errors=True)
        raise OSError('No benchmark file: %s' % benchfile)

    # Compare files
    diff = '\n'.join(difflib.unified_diff(bench, output,
        fromfile='benchmark', tofile='output')).strip()

    if diff:
        (root/'new').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(outfile), str(root/'new'/outfile.name))
        shutil.rmtree(outdir, ignore_errors=True)
        assert not(diff), 'Differences were found: {}\nplasTeX log:\n{}'.format(diff,  p.log)

    # Clean up
    shutil.rmtree(outdir, ignore_errors=True)

