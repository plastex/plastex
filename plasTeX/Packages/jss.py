
from plasTeX import Base

class Address(Base.Command):
    args = 'argument'
class Plaintitle(Base.Command):
    args = 'argument'
class Shorttitle(Base.Command):
    args = 'argument'
class Plainauthor(Base.Command):
    args = 'argument'

class Volume(Base.Command):
    args = 'argument'
class Year(Base.Command):
    args = 'argument'
class Month(Base.Command):
    args = 'argument'
class Issue(Base.Command):
    args = 'argument'

class Submitdate(Base.Command):
    args = 'argument'
class Acceptdate(Base.Command):
    args = 'argument'

class Abstract(Base.Command):
    args = 'argument'
class Keywords(Base.Command):
    args = 'argument'
class Plainkeywords(Base.Command):
    args = 'argument'

class Reviewer(Base.Command):
    args = 'argument'
class Booktitle(Base.Command):
    args = 'argument'
class Bookauthor(Base.Command):
    args = 'argument'
class Publisher(Base.Command):
    args = 'argument'
class Pubaddress(Base.Command):
    args = 'argument'
class Pubyear(Base.Command):
    args = 'argument'
class ISBN(Base.Command):
    args = 'argument'
class Pages(Base.Command):
    args = 'argument'
class Price(Base.Command):
    args = 'argument'
class Plainreviewer(Base.Command):
    args = 'argument'
class Softwaretitle(Base.Command):
    args = 'argument'

class Seriesname(Base.Command):
    args = 'argument'
class Hypersubject(Base.Command):
    args = 'argument'
class Hyperauthor(Base.Command):
    args = 'argument'
class Footername(Base.Command):
    args = 'argument'
class Firstdate(Base.Command):
    args = 'argument'
class Seconddate(Base.Command):
    args = 'argument'
class Reviewauthor(Base.Command):
    args = 'argument'

class code(Base.Command):
    args = 'argument'
class proglang(Base.Command):
    args = 'argument'
class pkg(Base.Command):
    args = 'argument'
class email(Base.Command):
    args = 'argument'
class doi(Base.Command):
    args = 'argument'
class E(Base.Command):
    args = 'argument'
class VAR(Base.Command):
    args = 'argument'
class COV(Base.Command):
    args = 'argument'
class Prob(Base.Command):
    args = 'argument'

class Sinput(Base.verbatim):pass
class Soutput(Base.verbatim):pass
class Scode(Base.verbatim):pass
class Code(Base.verbatim):pass
class CodeInput(Base.verbatim):pass
class CodeOutput(Base.verbatim):pass

class Schunk(Base.Environment):pass
class CodeChunk(Base.Environment):pass


