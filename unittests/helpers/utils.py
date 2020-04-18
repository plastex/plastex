import subprocess
import re

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
