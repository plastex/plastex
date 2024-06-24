from plasTeX.Base.LaTeX.Lists import List
from plasTeX import Environment
import re

class enumerate_(List):
    macroName = 'enumerate'
    args = '[ options:dict ]'
    def invoke(self, tex):
        # remember last counter before List.invoke resets it (if resume was used)
        if self.macroMode == Environment.MODE_BEGIN:
            lastCounter = int(self.ownerDocument.context.counters[List.counters[List.depth]])
        List.invoke(self,tex)

        # the rest is only useful when the environment starts
        if self.macroMode == Environment.MODE_END: return

        options = self.attributes.get('options',{})

        # start and resume options
        start = int(options.get('start', 1))
        if options.get('resume',False):
            start = lastCounter
        if start != 1:
            self.start=start
            self.ownerDocument.context.counters[List.counters[List.depth-1]].setcounter(int(start))

        # label style
        label = options.get('label','')
        if label:
            # FIXME: label is already expanded, so it does not contain \\alph etc anymore
            for cmd, style in [('\\alph','lower-alpha'),('\\Alph','alpha'),('\\arabic','decimal'),('\\roman','lower-roman'),('\\Roman','upper-roman')]:
                # might need regex (word end) but this is faster and will work for non-exotic cases
                if cmd in label:
                    self.list_style_type = style
                    break
            else:
                # warn that label was not recognized?
                pass
        else:
            # this should be active only with "shortlabels" package option
            k0=next(iter(options.keys())) # first dict key, i.e. first parameter
            v0=options[k0] # option value
            if v0==True: # if not true, value was explicitly given
                m=re.search(r'\b(?P<fmt>[aAIi1])\b',k0) # find isolated "tokens": i I a A 1
                if m:
                    self.list_style_type={'a':'lower-alpha','A':'upper-alpha','i':'lower-roman','I':'upper-roman','1':'decimal'}[m.group('fmt')]

        # TODO: handle more keywords and warn for those which are ignored (many)

