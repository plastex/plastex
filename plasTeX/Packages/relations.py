"""
The relations commands (uses and covers).
"""

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
        labels_dict = doc.context.labels
        used = [labels_dict[label] for label in self.attributes['labels']]
        node.setUserData('uses', used)
        depgraph = doc.userdata.get('depgraph', DepGraph())
        depgraph += [(node, used_node) for used_node in used]
        doc.setUserData('depgraph', depgraph)

class covers(Command):
    """ \covers{labels list} """
    args = 'labels:list:nox'

    def digest(self, tokens):
        Command.digest(self, tokens)
        node = self.parentNode
        labels_dict = self.ownerDocument.context.labels
        covered = [labels_dict[label] for label in self.attributes['labels']]
        node.setUserData('covers', covered)
        for covered_node in covered:
            covered_by = covered_node.userdata.get('covered_by', []) + [self]
            covered_node.setUserData('covered_by', covered_by)
