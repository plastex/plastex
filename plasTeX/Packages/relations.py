#!/usr/bin/env python

"""
The relations commands (uses and covers).
"""

from plastex import Command

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
