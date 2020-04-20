from plasTeX import Command, numToRoman

class romannumeral(Command):
    args = 'num:number'
    def invoke(self, tex):
        a = self.parse(tex)
        return tex.textTokens(numToRoman(a['num']).lower())
