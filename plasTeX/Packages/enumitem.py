from plasTeX.Base.LaTeX.Lists import List
class enumerate_(List):
    macroName = 'enumerate'
    args = '[ options:dict ]'
    def invoke(self, tex):
        List.invoke(self,tex)
        options = self.attributes.get('options',{})
        self.start = options.get('start', 0)
        if self.start != 0:
            self.ownerDocument.context.counters[List.counters[List.depth]].setcounter(int(self.start))
        # TODO: handle more keywords and warn for those which are ignored (many)
        # TODO (?): shortlabels package option, when first non-keyword
        #           (appears as ... = True in options:dict) is enumerate-package-style label style

