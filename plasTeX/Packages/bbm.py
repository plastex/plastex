from plasTeX import Command, sourceArguments

class mathbbm(Command):
    args = 'self'

    @property
    def source(self):
        return r'\mathbb{obj}'.format(obj=sourceArguments(self).strip())
