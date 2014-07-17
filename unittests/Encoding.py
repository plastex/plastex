#!/usr/bin/env python
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
        tex.input(ur'''\document{article}\begin{document}%s\end{document}''' % content)
        return tex.parse()

    def testString(self):
        # Bad character encoding
        locale.setlocale(locale.LC_ALL, "en_GB.iso8859-1")
        out = self.runDocument(u"é")

if __name__ == '__main__':
    unittest.main()

