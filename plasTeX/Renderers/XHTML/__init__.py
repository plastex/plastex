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

        # Remove empty paragraphs
        s = re.compile(r'<p>\s*</p>', re.I).sub(r'', s)

        # Add a non-breaking space to empty table cells
        s = re.compile(r'(<(td|th)\b[^>]*>)\s*(</\2>)', re.I).sub(r'\1&nbsp;\3', s)

        # MSIE is brain dead when it comes to alignment in table cells
        # when the table cells have different widths specified.  Rip out
        # all but the longest width in each column eqnarrays.
        def transpose(lists):
            if not lists: return []
            return map(lambda *row: list(row), *lists)

        def normalizeWidths(m):
            orig = m.group(0)
            begin, rows, end = m.group(1), m.group(2), m.group(3)
            widths = []
            rows = re.compile(r'(<tr\b[^>]*>.+?</tr>)', re.I|re.S).findall(rows)

            # Find the width of all cells
            for i, row in enumerate(rows):
                widths.append([])
                cells = re.compile(r'<td\b([^>]*)>.+?</td>', re.I|re.S).findall(row) 
                for j, cell in enumerate(cells):
                    m = re.search(r'\bwidth\s*:\s*((\d*\.?\d*)\s*[A-Za-z%]*)', cell)
                    if m:
                        widths[-1].append((float(m.group(2)),m.group(1)))
                    else:
                        widths[-1].append((0,'')) 

            # Get the maximum width for each column
            widths = [x[1] for x in max(widths)]

            # Apply those widths to the cells
            for i, row in enumerate(rows):
                cells = re.compile(r'(<td\b[^>]*>.+?</td>)', 
                                   re.I|re.S).findall(row) 
                for j, cell in enumerate(cells):
                    if j < len(widths) and not widths[j]:
                        continue
                    # Only apply width if it is on the cell
                    if not re.compile(r'<td\b[^>]*\bwidth:', re.S|re.I).search(cell):
                        continue
                    # Set the width to the widest width in the column
                    cells[j] = re.sub(r'(\bwidth\s*):\s*\d*\.?\d*\s*[A-Za-z%]*', 
                                      r'\1:%s' % widths[j], cell, 1)
                m = re.compile(r'(<tr\b[^>]*>)\s*.+?\s*(</tr>)', 
                                     re.S|re.I).search(row)
                rows[i] = '%s%s%s' % (m.group(1), '\n'.join(cells), m.group(2))

            return begin + '\n'.join(rows) + end

        s = re.compile(r'(<table\s+[^>]*class="eqnarray"[^>]*>\s*)(.+?)(\s*</table>)', re.I|re.S).sub(normalizeWidths, s)

        return s

Renderer = XHTML 
