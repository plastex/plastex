#!/usr/bin/env python

import os


def test_simple(tmpdir, renderXHTML, make_document):
    text = '''\\begin{alltt}\n   line 1\n   line 2\n   line 3\n\\end{alltt}'''
    lines = ['', '   line 1', '   line 2', '   line 3', '']

    # Test text content of node
    doc = make_document(packages='alltt', content=text)
    out = doc.getElementsByTagName('alltt')[0]

    plines = out.textContent.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

    # Test text content of rendering
    output = renderXHTML(tmpdir, doc)
    out = output.findAll('pre')[-1]

    plines = out.string.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)


def test_commands(tmpdir, renderXHTML, make_document):
    text = '''\\begin{alltt}\n   line 1\n   \\textbf{line} 2\n   \\textit{line 3}\n\\end{alltt}'''
    lines = ['', '   line 1', '   line 2', '   line 3', '']

    # Test text content of node
    doc = make_document(packages='alltt', content=text)
    out = doc.getElementsByTagName('alltt')[0]

    plines = out.textContent.split('\n')
    assert lines == plines, 'Content doesn\'t match - %s - %s' % (lines, plines)

    bf = out.getElementsByTagName('textbf')[0]
    assert bf.textContent == 'line', 'Bold text should be "line", but it is "%s"' % bf.textContent

    it = out.getElementsByTagName('textit')[0]
    assert it.textContent == 'line 3', 'Italic text should be "line 3", but it is "%s"' % it.textContent

    # Test rendering
    output = renderXHTML(tmpdir, doc)
    out = output.findAll('pre')[-1]

    assert out.b.string == 'line', 'Bold text should be "line", but it is "%s"' % out.b.string

    assert out.i.string == 'line 3', 'Italic text should be "line 3", but it is "%s"' % out.i.string
