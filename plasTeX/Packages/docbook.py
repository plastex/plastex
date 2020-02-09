from plasTeX import Base, Command


class DBsettitle(Command):
    args = 'self'

    def invoke(self, tex):
        super().invoke(tex)
        self.ownerDocument.userdata['set-title'] = self


class DBfirstterm(Command):
    args = 'self'
