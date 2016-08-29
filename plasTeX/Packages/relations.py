"""
The relations commands (uses and covers).
"""
import os
from jinja2 import Template

from plasTeX import Command



class DepGraph(list):
    pass

class uses(Command):
    """ \uses{labels list} """
    args = 'labels:list:nox'

    def digest(self, tokens):
        Command.digest(self, tokens)
        node = self.parentNode
        doc = self.ownerDocument
        def update_used():
            labels_dict = doc.context.labels
            used = [labels_dict[label] for label in self.attributes['labels']]
            node.setUserData('uses', used)
        doc.post_parse_cb.append(update_used)
        #depgraph = doc.userdata.get('depgraph', DepGraph())
        #depgraph += [(node, used_node) for used_node in used]
        #doc.setUserData('depgraph', depgraph)

class covers(Command):
    """ \covers{labels list} """
    args = 'labels:list:nox'

    def digest(self, tokens):
        Command.digest(self, tokens)
        node = self.parentNode
        doc = self.ownerDocument
        def update_covered():
            labels_dict = doc.context.labels
            covereds = [labels_dict[label] for label in self.attributes['labels']]
            node.setUserData('covers', covereds)
            for covered in covereds:
                covered_by = covered.userdata.get('covered_by', [])
                covered.setUserData('covered_by', covered_by + [node])
        doc.post_parse_cb.append(update_covered)

class proves(Command):
    """ \proves{label} """
    args = 'label:str'

    def digest(self, tokens):
        Command.digest(self, tokens)
        node = self.parentNode
        doc = self.ownerDocument
        def update_proved():
            labels_dict = doc.context.labels
            proved = labels_dict[self.attributes['label']]
            node.setUserData('proves', proved)
            proved.userdata['proved_by'] = node
        doc.post_parse_cb.append(update_proved)


class ThmReport(object):
    """"""

    def __init__(self, id, caption, statement, covered_by):
        """Constructor for ThmReport"""
        self.id = id
        self.caption = caption
        self.statement = statement
        self.covered_by = covered_by

    @classmethod
    def from_thm(cls, thm):
        covered_by = thm.userdata.get('covered_by', [])
        caption = thm.caption + ' ' + thm.ref
        return cls(thm.id, caption, unicode(thm), covered_by)


class PartialReport(object):
    def __init__(self, title, nb_thms, nb_not_covered, thm_reports):
        self.nb_thms = nb_thms
        self.nb_not_covered = nb_not_covered
        self.coverage = 100 * (nb_thms - nb_not_covered) / nb_thms if nb_thms else 100
        self.thm_reports = thm_reports
        self.title = title
        if self.coverage == 100:
            self.status = 'ok'
        elif self.coverage > 0:
            self.status = 'partial'
        else:
            self.status = 'void'

    @classmethod
    def from_section(cls, section, thm_types):
        nb_thms = 0
        nb_not_covered = 0
        thm_reports = []
        theorems = []
        for thm_type in thm_types:
            theorems += section.getElementsByTagName(thm_type)
        for thm in theorems:
            nb_thms += 1
            thm_report = ThmReport.from_thm(thm)
            if not thm_report.covered_by:
                nb_not_covered += 1
            thm_reports.append(thm_report)
        return cls(section.fullTocEntry, nb_thms, nb_not_covered, thm_reports)


class Report():
    """A full report."""

    def __init__(self, partials):
        """Constructor for Report"""
        self.partials = partials
        self.nb_thms = sum([p.nb_thms for p in partials])
        self.nb_not_covered = sum([p.nb_not_covered for p in partials])
        self.coverage = 100 * (self.nb_thms - self.nb_not_covered) / self.nb_thms if self.nb_thms else 100


def ProcessOptions(options, document):
    """This is called when the package is loaded."""

    document.userdata.setdefault('pkg_override', []).append('relations')

    coverage_file = options.get('coverage')
    if coverage_file:
        with open(coverage_file+'.j2') as src:
            tpl = Template(src.read())
        outdir = document.config['files']['directory']
        outfile = os.path.join(outdir, coverage_file)+'.html'

        thm_types = [thm.strip() for thm in options.get('thms', '').split('+')]
        section = options.get('section', 'chapter')

        def make_coverage_report(document):
            sections = document.getElementsByTagName(section)
            report = Report([PartialReport.from_section(sec, thm_types) for sec in sections])
            tpl.stream(report=report, config=document.config).dump(outfile)
            return [coverage_file+'.html']

        document.userdata.setdefault('precleanup_cbs', []).append(make_coverage_report)

