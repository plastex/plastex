#!/usr/bin/env python

from Generic import GenericOption, GenericParser, GenericArgument
from plasTeX.ConfigManager import InvalidOptionError

class IntegerParser(GenericParser): pass

class IntegerOption(IntegerParser, GenericOption):
   """ Integer configuration option """

   synopsis = 'n'

   def cast(self, data):
      name = self.name
      if self.actual: name = self.actual
      if data is None: return
      try: return int(data)
      except: raise InvalidOptionError(name, data, type='int')


class IntegerArgument(GenericArgument, IntegerOption):
   """ Integer command-line argument """
