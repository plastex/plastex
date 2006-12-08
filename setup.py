#!/usr/bin/env python

from distutils.core import setup

templates = ['*.html','*.htm','*.xml','*.zpt','*.zpts']
images = ['*.gif','*.png','*.jpg','*.jpeg','*.js']
styles = ['*.css']

setup(name="plasTeX",
      description="LaTeX document processing framework",
      author="Kevin D. Smith",
      author_email="Kevin.Smith@sas.com",
      #url="",
      packages = [
         'plasTeX',
         'plasTeX.Base',
         'plasTeX.Base.LaTeX',
         'plasTeX.Base.LaTeX.Languages',
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
         'plasTeX.Renderers.ZPT',
         'plasTeX.Renderers.PageTemplate',
         'plasTeX.Renderers.PageTemplate.simpletal',
         'plasTeX.Renderers.S5',
         'plasTeX.Renderers.S5.Themes',
         'plasTeX.Renderers.S5.Themes.default',
      ],
      package_data = {
         'plasTeX.Base.LaTeX': ['*.xml','*.txt'],
         'plasTeX.Renderers.XHTML': templates,
         'plasTeX.Renderers.XHTML.Themes.default': templates,
         'plasTeX.Renderers.XHTML.Themes.default.icons': images,
         'plasTeX.Renderers.XHTML.Themes.default.styles': styles,
         'plasTeX.Renderers.XHTML.Themes.python': templates+styles,
         'plasTeX.Renderers.XHTML.Themes.python.icons': images,
         'plasTeX.Renderers.XHTML.Themes.plain': templates,
      },
      scripts=['plasTeX/plastex','plasTeX/Imagers/cgpdfpng'],
)
