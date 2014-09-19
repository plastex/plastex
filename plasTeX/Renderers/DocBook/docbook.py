from plasTeX import Command
from plasTeX.Base.LaTeX import table as Ptable, tabular as Ptabular

def get_see(term):
    see = None
    seealso = None
    if term.find('|') != -1:
        term, fmt = term.split('|')
        if fmt.find('seealso') != -1:
            seealso = fmt
        elif fmt.find('see') != -1:
            see = fmt

    return term, see, seealso

def parse_indexentry(s):
    term = s
    sortstr = None
    if term.find('@') != -1:
        term, sortstr = term.split('@')
    term, see, seealso = get_see(term)
    return (term, sortstr, see, seealso)

class table(Ptable):

    class tabular(Ptabular):
        args = '[ pos:str ] colspec:nox'
        templateName = 'doctabular'


class bibname(Command): pass

class chaptername(Command): pass
class thechapter(Command): pass

class sectionname(Command): pass
class thesection(Command): pass

class subsectionname(Command): pass
class thesubsection(Command): pass

class figurename(Command): pass
class thefigure(Command): pass

class theenumi(Command): pass

class textsubscript(Command):
    args = 'argument'

class textsuperscript(Command):
    args = 'argument'

class uppercase(Command):
    args = 'argument:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        self.attributes['argument'] = self.attributes['argument'].upper()

class index(Command):
    args = 'argument:str'

    def invoke(self, tex):
        Command.invoke(self, tex)
        entry = self.attributes['argument']
        if entry.find('!') != -1:
            primary, secondary = entry.split('!')

            primary, prisort, see, seealso= parse_indexentry(primary)
            if see or seealso:
                secondary, secsort, _, _ = parse_indexentry(secondary)
            else:
                secondary, secsort, see, seealso = parse_indexentry(secondary)
        else:
            primary, prisort, see, seealso = parse_indexentry(entry)

        self.data = {
            'primary': primary,
            'secondary':secondary,
            'prisort': prisort,
            'secsort': secsort,
            'see': see,
            'seealso': seealso,
            }
