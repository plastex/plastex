#!/usr/bin/env python

from Generic import GenericOption, GenericParser, GenericArgument
from plasTeX.ConfigManager import InvalidOptionError


class FloatParser(GenericParser): pass

class FloatOption(FloatParser, GenericOption):
   """ Float configuration option """

   synopsis = 'num'

   def cast(self, data):
      name = self.name
      if self.actual: name = self.actual
      if data is None: return
      try: return float(data)
      except: raise InvalidOptionError(name, data, type='float')


class FloatArgument(GenericArgument, FloatOption):
   """ Float command-line argument """
