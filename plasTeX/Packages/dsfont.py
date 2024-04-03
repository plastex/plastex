from plasTeX import Command, sourceArguments


class mathds(Command):
    args = 'self'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
