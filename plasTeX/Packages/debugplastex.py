import pdb

from plasTeX import Command

class settrace(Command):
    def invoke(self, tex):
        pdb.set_trace()
