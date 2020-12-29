from plasTeX import VerbatimEnvironment

def ProcessOptions(options, document):
    document.config['images']['scales'].setdefault('tikzcd', 1.5)

class tikzcd(VerbatimEnvironment):
    pass
