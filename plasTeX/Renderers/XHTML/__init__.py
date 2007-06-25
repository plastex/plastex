#!/usr/bin/env python

import sys, os, re, codecs, plasTeX
from plasTeX.Renderers.PageTemplate import Renderer as _Renderer

class XHTML(_Renderer):
    """ Renderer for XHTML documents """

    fileExtension = '.html'
    imageTypes = ['.png','.jpg','.jpeg','.gif']
    vectorImageTypes = ['.svg']

    def processFileContent(self, document, s):
        s = _Renderer.processFileContent(self, document, s)

        # Force XHTML syntax on empty tags
        s = re.compile(r'(<(?:hr|br|img|link|meta)\b.*?)\s*/?\s*(>)', 
                       re.I|re.S).sub(r'\1 /\2', s)

        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I|re.S).sub(r'\1&nbsp;\3', s)

        # Realign eqnarray.  The cells in an eqnarry can really have some
        # deep depths.  This causes the content of those cells to overlap
        # the content below them.  Therefore, all cells in an eqnarray
        # are pulled up by the amount of the deepest depth.
        def normalizeBottom(m):
            begin, rows, end = m.group(1), m.group(2), m.group(3)
            rows = re.compile(r'(<tr\b[^>]*>.+?</tr>)', re.I|re.S).findall(rows)
            newrows = []
            for i, row in enumerate(rows):
                bottoms = {}
                for amount, unit in re.compile(r'(?:\'|"|;)\s*bottom\s*:\s*(-?[\d\.]+)\s*(\w*)', re.I).findall(row):
                    if unit not in bottoms:
                        bottoms[unit] = []
                    bottoms[unit].append(float(amount))
                for unit in bottoms:
                    adjust = -min(bottoms[unit])
                    row = re.compile(r'((?:\'|"|;)\s*bottom\s*:\s*)(-?[\d\.]+)\s*%s' % unit, re.I).sub(lambda x: x.group(1) + str(float(x.group(2)) + adjust) + unit, row)
                newrows.append(row)
            return begin + u''.join(newrows) + end

        s = re.compile(r'(<table\s+[^>]*class="eqnarray"[^>]*>\s*)(.+?)(\s*</table>)', re.I|re.S).sub(normalizeBottom, s)

        return s

Renderer = XHTML 
