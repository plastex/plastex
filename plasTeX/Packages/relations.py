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
