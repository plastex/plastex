import subprocess
import re
from pathlib import Path
import os
from plasTeX.TeX import TeX
from tempfile import TemporaryDirectory
from hashlib import md5

CACHE_LOCATION = Path(__file__).absolute().parent / "compare_cache"

def cmp_img(a: str, b: str) -> float:
    out = subprocess.run(["compare", "-quiet", "-metric", "MSE",
        '-subimage-search', a, b, "/dev/null"],
        stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, check=False)

    # return code 1 is for dissimilar images, but we use our own threshold
    # since imagemagick is too strict
    if out.returncode == 2:
        class CompareError(Exception):
            def __init__(self, message):
                self.message = message
        out = subprocess.run(["compare", "-verbose", "-metric", "MSE",
            '-subimage-search', a, b, "/dev/null"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL,
            check=False)
        print(out.stdout.decode())
        print(out.stderr.decode())

        raise CompareError("Compare failed on {}, {}".format(a, b))

    # The result is b"... (diff)"
    output = out.stderr.decode()
    m = re.match(r'[^(]*\(([^)]*)\)', output)
    if not m:
        raise CompareError("Can't parse compare output {}".format(output))
    diff = m.group(1)

    # out.stderr is a byte sequence, but float can take byte sequences
    return float(diff)

def compare_output(tex: str):
    r"""
    This checks whether plastex produces the same output as tex. This only works
    for things with simple plain text output, and is intended to be used for
    testing primitives such as \let, \def, \expandafter etc.
    """
    if not CACHE_LOCATION.is_dir():
        CACHE_LOCATION.mkdir()

    cwd = os.getcwd()
    try:
        plastex_out = TeX().input(tex).parse().textContent.strip()
        tex_hash = md5(tex.encode('utf-8')).hexdigest()
        tex_out = None
        try:
            tex_out = (CACHE_LOCATION / tex_hash).read_text()
        except IOError:
            with TemporaryDirectory() as tmpdir:
                os.chdir(tmpdir)

                if r'\documentclass{article}' not in tex:
                    tex = r'\documentclass{article}\usepackage{microtype}\DisableLigatures{encoding = *, family = *}\begin{document}' + tex + r'\end{document}'
                tex = r'\nonstopmode\AtBeginDocument{\thispagestyle{empty}}' + tex

                with open("test.tex", "w") as f:
                    f.write(tex)

                subprocess.run(["pdflatex", "test.tex"], check=True)
                if not os.path.exists("test.pdf"):
                    # If pdflatex was successful but a pdf file was not produced,
                    # this means 0 pages were produced, so the content is empty.
                    return plastex_out.strip() == ""

                out = subprocess.run(
                        ["gs", "-q", "-sDEVICE=txtwrite", "-o", "%stdout%", "test.pdf"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stdin=subprocess.DEVNULL,
                        universal_newlines=True)
                tex_out = out.stdout.strip()
                (CACHE_LOCATION / tex_hash).write_text(tex_out)

        assert plastex_out == tex_out, ('%r != %r ' % (plastex_out, tex_out))
    finally:
        os.chdir(cwd)
