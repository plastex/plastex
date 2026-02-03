import unittest, re
from unittest import TestCase
from plasTeX.TeX import TeX
from plasTeX import Macro

def normalize(s):
    return re.sub(r'\s+', r' ', s).strip()


class Source(TestCase):
    def testXYMatrix(self):
        input = r'\xymatrix{A \ar[d]^b \ar[r]^a &B\ar[d]^c\\ C \ar[r]^d &D}'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input.replace(" ", "") == source.replace(" ", ""), '"%s" != "%s"' % (input, source)

    def testXYMatrix2(self):
        input = r'\xymatrix{A \ar@{->>}[rd] \ar@{^{(}->}[r]&B \ar@{.>}[d]&C \ar@{_{(}->}[l]\ar@{->>}[ld]\\&D}'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input.replace(" ", "") == source.replace(" ", ""), '"%s" != "%s"' % (input, source)

    def testXYMatrix3(self):
        input = r'\xymatrix{A \ar[r]^u_d \ar[rd]^u_d &B \ar[d]^u_d &C \ar[l]^u_d \ar[ld]^u_d\\&D}'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input.replace(" ", "") == source.replace(" ", ""), '"%s" != "%s"' % (input, source)

    def testList(self):
        input = r'\begin{enumerate} \item one \item two \item three \end{enumerate}'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)

        input = r'\item one'
        item = output[0].firstChild
        source = normalize(item.source)
        assert input == source, '"%s" != "%s"' % (input, source)

    def testMath(self):
        input = r'a $ x^{y_3} $ b'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)

    def testMathCal(self):
        input = r'a $ \mathcal A $ b'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)

    def testDisplayMath(self):
        input = r'a \[ x^{y_3} \]b'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)
    
        # \begin{displaymath} ... \end{displaymath} is transformed
        # into \[ ...\] 
        input2 = r'a \begin{displaymath} x^{y_3} \end{displaymath}b'
        s = TeX()
        s.input(input2)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)

    def testSection(self):
        input = r'\section{Heading 1} foo one \subsection{Heading 2} bar two'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)
     
        input = r'\subsection{Heading 2} bar two'
        item = output[0].lastChild
        source = normalize(item.source)
        assert input == source, '"%s" != "%s"' % (input, source)

    def testTabular(self):
        input = r'\begin{tabular}{lll} \hline a & b & c \\[0.4in] 1 & 2 & 3 \end{tabular}'
        s = TeX()
        s.input(input)
        output = s.parse()
        source = normalize(output.source)
        assert input == source, '"%s" != "%s"' % (input, source)
        
    def testRenewcommand(self):
        input = r'\renewcommand{\t}{test}\renewcommand\u{more}'
        s = TeX()
        s.input(input)
        output = s.parse()
        assert output.source == input

if __name__ == '__main__':
    unittest.main()

