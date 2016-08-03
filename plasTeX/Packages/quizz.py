"""
Make quizzes.
"""

from plasTeX.Base.LaTeX.Lists import List
from plasTeX import Command, Environment


class quizz(List):
    class wrong(List.item):
        pass

    class right(List.item):
        pass

    class question(Command):
        args = 'self'

        def digest(self, tokens):
            Command.digest(self, tokens)
            node = self.parentNode
            node.userdata['question'] = self

    def digest(self, tokens):
        List.digest(self, tokens)
        node = self.parentNode
        quizzes = node.userdata.get('quizzes', [])
        quizzes.append(self)
        node.userdata['quizzes'] = quizzes
