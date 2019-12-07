#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

templates = ['*.html','*.htm','*.xml','*.zpt','*.zpts','*.jinja2','*.jinja2s']
images = ['*.gif','*.png','*.jpg','*.jpeg','*.js','*.htc','*.svg']
styles = ['*.css']
javascript = ['*.js']

setup(name="plasTeX",
      description="LaTeX document processing framework",
      long_description = long_description,
      long_description_content_type="text/markdown",
      version="2.1",
      author="Kevin D. Smith",
      author_email="Kevin.Smith@sas.com",
      url="https://github.com/plastex/plastex",
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
      python_requires='>=3.5',
      packages = [
         'plasTeX',
         'plasTeX.Base',
         'plasTeX.Base.LaTeX',
         'plasTeX.Base.TeX',
         'plasTeX.ConfigManager',
         'plasTeX.DOM',
         'plasTeX.Imagers',
         'plasTeX.Packages',
         'plasTeX.Renderers',
         'plasTeX.Renderers.XHTML',
         'plasTeX.Renderers.XHTML.Themes',
         'plasTeX.Renderers.XHTML.Themes.default',
         'plasTeX.Renderers.XHTML.Themes.default.icons',
         'plasTeX.Renderers.XHTML.Themes.default.styles',
         'plasTeX.Renderers.XHTML.Themes.python',
         'plasTeX.Renderers.XHTML.Themes.python.icons',
         'plasTeX.Renderers.XHTML.Themes.plain',
         'plasTeX.Renderers.XHTML.Themes.minimal',
         'plasTeX.Renderers.HTML5',
         'plasTeX.Renderers.HTML5.Themes',
         'plasTeX.Renderers.HTML5.Themes.default',
         'plasTeX.Renderers.HTML5.Themes.default.styles',
         'plasTeX.Renderers.HTML5.Themes.default.js',
         'plasTeX.Renderers.DocBook',
         'plasTeX.Renderers.DocBook.Themes',
         'plasTeX.Renderers.DocBook.Themes.default',
         'plasTeX.Renderers.DocBook.Themes.book',
         'plasTeX.Renderers.DocBook.Themes.article',
         'plasTeX.Renderers.ManPage',
         'plasTeX.Renderers.Text',
         'plasTeX.Renderers.ZPT',
         'plasTeX.Renderers.PageTemplate',
         'plasTeX.Renderers.PageTemplate.simpletal',
         'plasTeX.Renderers.S5',
         'plasTeX.Renderers.S5.Themes',
         'plasTeX.Renderers.S5.Themes.default',
         'plasTeX.Renderers.S5.Themes.default.ui',
         'plasTeX.Renderers.S5.Themes.default.ui.default',
      ],
      package_data = {
         'plasTeX': ['*.xml', 'plasTeXrc'],
         'plasTeX.Base.LaTeX': ['*.xml','*.txt'],
         'plasTeX.Renderers.DocBook': templates,
         'plasTeX.Renderers.DocBook.Themes.default': templates,
         'plasTeX.Renderers.DocBook.Themes.book': templates,
         'plasTeX.Renderers.DocBook.Themes.article': templates,
         'plasTeX.Renderers.XHTML': templates,
         'plasTeX.Renderers.XHTML.Themes.default': templates,
         'plasTeX.Renderers.XHTML.Themes.default.icons': images,
         'plasTeX.Renderers.XHTML.Themes.default.styles': styles,
         'plasTeX.Renderers.XHTML.Themes.minimal': templates,
         'plasTeX.Renderers.XHTML.Themes.python': templates+styles,
         'plasTeX.Renderers.XHTML.Themes.python.icons': images,
         'plasTeX.Renderers.XHTML.Themes.plain': templates,
         'plasTeX.Renderers.HTML5': templates,
         'plasTeX.Renderers.HTML5.Themes.default': templates+images,
         'plasTeX.Renderers.HTML5.Themes.default.styles': styles,
         'plasTeX.Renderers.HTML5.Themes.default.js': javascript,
         'plasTeX.Renderers.S5': templates,
         'plasTeX.Renderers.S5.Themes.default': templates,
         'plasTeX.Renderers.S5.Themes.default.ui.default': templates+styles+images,
      },
      scripts=['plasTeX/plastex'],
)
