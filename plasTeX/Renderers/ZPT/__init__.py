#!/usr/bin/env python

"""
ZPT - Zope Page Template Renderer

This module contains a plasTeX renderer that uses Zope Page Templates
(actually simpleTAL) as the templating engine.

NOTE: This module isn't really needed any more.  The PageTempate 
renderer does everything that this module did and more.  This is 
just here for backwards compatibility.

"""

from plasTeX.Renderers.PageTemplate import Renderer

class ZPT(Renderer):
    pass

Renderer = ZPT
