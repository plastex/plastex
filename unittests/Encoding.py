# -*- coding: utf-8 -*-

import locale
import unittest
from plasTeX.TeX import TeX

class Longtables(unittest.TestCase):

    def runDocument(self, content):
        """
        Compile a document with the given content

        Arguments:
        content - string containing the content of the document

        Returns: TeX document

        """
        tex = TeX()
        tex.disableLogging()
        tex.input(r'\document{article}\begin{document}%s\end{document}' % content)
        return tex.parse()

    def testString(self):
        # Test that reading a document containing accents raises no exception
        # even when the current locale does not support accents.
        loc = locale.getlocale(locale.LC_CTYPE)
        # Bad character encoding
        locale.setlocale(locale.LC_CTYPE, "C")
        self.runDocument(u"é")
        locale.setlocale(locale.LC_CTYPE, loc)

if __name__ == '__main__':
    unittest.main()

