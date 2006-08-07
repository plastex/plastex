#!/usr/bin/env python

import os
from plasTeX import Command

from graphics import DeclareGraphicsExtensions
from graphics import includegraphics as ig

class includegraphics(ig):
    args = '[ options:dict ] file:str'
    packageName = 'graphicx'
